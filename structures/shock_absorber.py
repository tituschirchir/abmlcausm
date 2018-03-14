class BankWrapper:
    def __init__(self, bank):
        self.bank = bank
        self.debt = bank.balance_sheet.find_node_series("Assets", "Interbank").value
        self.credit = bank.balance_sheet.find_node_series("Liabilities", "Interbank").value

    def allocate_debt(self):
        debt_node = self.bank.balance_sheet.find_node_series("Assets", "Interbank").value
        total_debt = sum([x.node_to.allocated_credit for x in self.bank.edges])
        to_be_shared = min(debt_node, total_debt)
        if total_debt > 0.0:
            for edge in self.bank.edges:
                d2 = to_be_shared * edge.node_to.allocated_credit / total_debt
                edge.value += d2
                edge.node_to.allocated_credit -= d2
                self.debt -= d2


class ExposureAllocator:
    def __init__(self, banks):
        self.banks = banks
        self.wrappers = [BankWrapper(x) for x in self.banks]
        self.other_banks_exposure = 0.0

    # Allocate debt and credit in batches to avoid overallocation to one entity
    def disburse_exposure(self):
        [wb.allocate_debt() for wb in self.wrappers]
