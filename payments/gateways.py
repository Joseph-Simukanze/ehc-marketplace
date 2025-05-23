# payments/gateways.py

class MTNPaymentGateway:
    def initiate_payment(self, phone_number, amount, transaction_id):
        # logic to initiate payment with MTN
        return {'status': 'SUCCESS', 'message': 'Payment initiated with MTN'}

    def check_payment_status(self, transaction_id):
        # Logic to check payment status using MTN's API
        # For example, simulate a response:
        response = {
            'status': 'SUCCESS',
            'message': 'Payment confirmed with MTN for transaction {}'.format(transaction_id)
        }
        return response

class AirtelPaymentGateway:
    def initiate_payment(self, phone_number, amount, transaction_id):
        # logic to initiate payment with Airtel
        return {'status': 'SUCCESS', 'message': 'Payment initiated with Airtel'}

    def check_payment_status(self, transaction_id):
        # Logic to check payment status using Airtel's API
        # Simulated response:
        response = {
            'status': 'SUCCESS',
            'message': 'Payment confirmed with Airtel for transaction {}'.format(transaction_id)
        }
        return response
