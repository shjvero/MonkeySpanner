import os, sys, csv

from .rstr_record import RSTRRecord
from .rcrd_record import RCRDRecord
from .transaction import Transaction


class LogFile:
    def __init__(self, dump_dir=None, file_name=None, cluster_size=4096, performance=False):
        self.dump_dir = os.getcwd()
        self.file_name = file_name
        self.cluster_size = cluster_size
        self.performance = performance
        self.rstr_records = []
        self.buff_records = []
        self.rcrd_records = []
        self.prev_lsn_index = {}
        self.this_lsn_index = {}
        self.lsns = {}
        self.transactions = {}
        self.faulty_transactions = []
        self.error_start_from_offset = 0
        self.error_discard_data = 0
        self.invalid_page_count = 0
        self.page_count = 0
        self.total_entries = 0

        if dump_dir:
            dump_path = os.path.join(os.getcwd(), dump_dir)
            if not os.path.exists(dump_path):
                os.makedirs(dump_path)
            self.dump_dir = dump_path

    ####################################################################################################################
    # class functions
    def parse_all(self, num=None):
        if num: num += 3
        with open(self.file_name, 'rb') as f:
            # first and second RSTR record
            for x in range(1, 3):
                rstr_record = RSTRRecord(f.read(self.cluster_size))
                self.rstr_records.append(rstr_record)
            # first and second Buffer Pages
            for x in range(1, 3):
                buff_record = RCRDRecord(f.read(self.cluster_size), x, self.dump_dir)
                self.buff_records.append(buff_record)
            i = 3
            prev_page = RCRDRecord(f.read(self.cluster_size), i, self.dump_dir)
            self.add_if_valid(prev_page)
            self.keep_count(prev_page)
            while True:
                buffer = f.read(self.cluster_size)
                if len(buffer) != self.cluster_size:
                    break
                else:
                    i += 1
                    curr_page = RCRDRecord(buffer, i, self.dump_dir, prev_page.leftover)
                    self.add_if_valid(curr_page)
                    prev_page = curr_page
                    if i == num:
                        break

    def connect_transactions(self):
        transaction_num = 0
        while len(self.this_lsn_index) > 0:
            # Pick an arbitrary lsn from the index
            _, kickoff_lsn_tuple = self.this_lsn_index.popitem()
            transaction = Transaction(kickoff_lsn_tuple)

            # Start expanding the transaction to the left as long as the transaction thinks it's not done
            left_lsn_tuple = kickoff_lsn_tuple
            while transaction.continue_left:
                try:
                    key = left_lsn_tuple[0].previous_lsn
                    left_lsn_tuple = self.this_lsn_index.pop(key)
                    transaction.prepend(left_lsn_tuple)
                except KeyError:
                    # print('error left ', kickoff_lsn_tuple[0].this_lsn, key)
                    break

            # Start expanding the transcation to the right as long as the transaction thinks it's not done
            right_lsn_tuple = kickoff_lsn_tuple
            while transaction.continue_right:
                try:
                    key = right_lsn_tuple[0].this_lsn
                    right_lsn_tuple = self.prev_lsn_index.pop(key)
                    transaction.append(right_lsn_tuple)
                    try:
                        self.this_lsn_index.pop(right_lsn_tuple[0].this_lsn)
                    except Exception as e:
                        # print('error right right', kickoff_lsn_tuple[0].this_lsn, e)
                        pass
                except KeyError:
                    # print('error right', kickoff_lsn_tuple[0].this_lsn, key)
                    break

            if transaction.is_correct:
                key = transaction.mft_key
                self.transactions[key] = transaction
            else:
                self.faulty_transactions.append(transaction)
            transaction.transaction_num = transaction_num
            transaction.attach_transaction_number_to_lsns()
            transaction_num += 1

    def export_transactions(self, export_file=None):
        if not self.rcrd_records:
            return
        if export_file:
            with open(export_file, 'w') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(Transaction.format_csv_column_headers())
                for transaction in self.transactions.values():
                    csv_writer.writerow(transaction.format_csv())
                for transaction in self.faulty_transactions:
                    csv_writer.writerow(transaction.format_csv())
        else:
            csv_writer = csv.writer(sys.stdout)
            csv_writer.writerow(Transaction.format_csv_column_headers())
            for transaction in self.transactions.values():
                csv_writer.writerow(transaction.format_csv())
            for transaction in self.faulty_transactions:
                csv_writer.writerow(transaction.format_csv())

    def export_parsed_lsns(self, export_file=None, lsn_numbers=None):
        if export_file:
            with open(export_file, 'w') as f:
                # Case when no specific lsns are requested. Export all of them.
                if not lsn_numbers:
                    for tup in self.lsns.values():
                        self.export_parsed_lsn(tup=tup, out=f)
                # Specific set of lsns requested. Export only those.
                else:
                    for lsn in lsn_numbers:
                        tup = self.lsns[lsn]
                        self.export_parsed_lsn(tup=tup, out=f)
        else:
            # Case when no specific lsns are requested. Export all of them.
            if not lsn_numbers:
                for tup in self.lsns.values():
                    self.export_parsed_lsn(tup=tup, out=sys.stdout)
            # Specific set of lsns requested. Export only those.
            else:
                for lsn in lsn_numbers:
                    tup = self.lsns[lsn]
                    self.export_parsed_lsn(tup=tup, out=sys.stdout)

    # add if page has valid page header
    def add_if_valid(self, page):
        if page.header.magic_number != 'RCRD':
            self.invalid_page_count += 1
        else:
            self.count_errors_in_page(page.error)
            self.keep_count(page)
            self.rcrd_records.append(page)

            for lsn_header, lsn_content in page.lsn_entries:
                if lsn_header.previous_lsn:
                    self.prev_lsn_index[lsn_header.previous_lsn] = (lsn_header, lsn_content)
                self.this_lsn_index[lsn_header.this_lsn] = (lsn_header, lsn_content)
                self.lsns[lsn_header.this_lsn] = (lsn_header, lsn_content)

    # keep count of the number of pages and total entries
    def keep_count(self, page):
        self.page_count += 1
        self.total_entries += page.entry_count

    # function that keeps track of the error counts
    def count_errors_in_page(self, error):
        if error == 1:
            self.error_start_from_offset += 1
        elif error > 1:
            self.error_discard_data += 1
