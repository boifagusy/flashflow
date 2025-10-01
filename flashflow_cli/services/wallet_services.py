"""
FlashFlow Wallet and Referrals Services
=====================================

Comprehensive wallet and referral system for FlashFlow applications.
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, asdict
import hashlib
import logging

logger = logging.getLogger(__name__)

@dataclass
class Wallet:
    """Represents a user wallet"""
    id: str
    user_id: str
    balance: Decimal = Decimal('0.00')
    currency: str = 'USD'
    status: str = 'active'  # active, frozen, closed
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if isinstance(self.balance, (int, float)):
            self.balance = Decimal(str(self.balance))

@dataclass
class Transaction:
    """Represents a wallet transaction"""
    id: str
    wallet_id: str
    amount: Decimal
    currency: str
    type: str  # deposit, withdrawal, transfer, refund, bonus
    status: str  # pending, completed, failed, cancelled
    description: str = ''
    reference_id: str = ''
    fee: Decimal = Decimal('0.00')
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.amount, (int, float)):
            self.amount = Decimal(str(self.amount))
        if isinstance(self.fee, (int, float)):
            self.fee = Decimal(str(self.fee))

@dataclass
class Referral:
    """Represents a referral relationship"""
    id: str
    referrer_id: str  # user who referred
    referee_id: str   # user who was referred
    status: str = 'pending'  # pending, converted, expired
    reward_amount: Decimal = Decimal('0.00')
    currency: str = 'USD'
    referral_code: str = ''
    created_at: datetime = None
    converted_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if isinstance(self.reward_amount, (int, float)):
            self.reward_amount = Decimal(str(self.reward_amount))
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
    
    def _generate_referral_code(self) -> str:
        """Generate a unique referral code"""
        return hashlib.sha256(f"{self.referrer_id}{self.created_at}".encode()).hexdigest()[:8].upper()

@dataclass
class ReferralProgram:
    """Represents a referral program configuration"""
    id: str
    name: str
    description: str
    reward_amount: Decimal
    currency: str = 'USD'
    reward_type: str = 'fixed'  # fixed, percentage
    minimum_purchase: Decimal = Decimal('0.00')
    expiration_days: int = 30
    max_referrals_per_user: int = 10
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if isinstance(self.reward_amount, (int, float)):
            self.reward_amount = Decimal(str(self.reward_amount))
        if isinstance(self.minimum_purchase, (int, float)):
            self.minimum_purchase = Decimal(str(self.minimum_purchase))

class WalletManager:
    """Main wallet management service"""
    
    def __init__(self):
        self.wallets: Dict[str, Wallet] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.referrals: Dict[str, Referral] = {}
        self.referral_programs: Dict[str, ReferralProgram] = {}
        self._load_default_program()
    
    def _load_default_program(self):
        """Load default referral program"""
        default_program = ReferralProgram(
            id='default',
            name='Default Referral Program',
            description='Earn rewards for referring friends',
            reward_amount=Decimal('10.00'),
            currency='USD',
            reward_type='fixed',
            minimum_purchase=Decimal('25.00'),
            expiration_days=30,
            max_referrals_per_user=10,
            is_active=True
        )
        self.referral_programs['default'] = default_program
    
    def create_wallet(self, user_id: str, currency: str = 'USD') -> Wallet:
        """Create a new wallet for a user"""
        try:
            wallet_id = str(uuid.uuid4())
            wallet = Wallet(
                id=wallet_id,
                user_id=user_id,
                currency=currency
            )
            self.wallets[wallet_id] = wallet
            logger.info(f"Created wallet {wallet_id} for user {user_id}")
            return wallet
        except Exception as e:
            logger.error(f"Failed to create wallet for user {user_id}: {e}")
            raise
    
    def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        """Get wallet by ID"""
        return self.wallets.get(wallet_id)
    
    def get_user_wallet(self, user_id: str, currency: str = 'USD') -> Optional[Wallet]:
        """Get user's wallet by user ID and currency"""
        for wallet in self.wallets.values():
            if wallet.user_id == user_id and wallet.currency == currency:
                return wallet
        return None
    
    def deposit(self, wallet_id: str, amount: Union[Decimal, float, int], 
                description: str = '', reference_id: str = '') -> Transaction:
        """Deposit funds into a wallet"""
        try:
            wallet = self.get_wallet(wallet_id)
            if not wallet:
                raise ValueError(f"Wallet {wallet_id} not found")
            
            if isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            
            if amount <= 0:
                raise ValueError("Deposit amount must be positive")
            
            # Create transaction
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                id=transaction_id,
                wallet_id=wallet_id,
                amount=amount,
                currency=wallet.currency,
                type='deposit',
                status='completed',
                description=description,
                reference_id=reference_id
            )
            
            # Update wallet balance
            wallet.balance += amount
            wallet.updated_at = datetime.utcnow()
            
            # Store transaction
            self.transactions[transaction_id] = transaction
            
            logger.info(f"Deposited {amount} {wallet.currency} to wallet {wallet_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to deposit to wallet {wallet_id}: {e}")
            raise
    
    def withdraw(self, wallet_id: str, amount: Union[Decimal, float, int], 
                 description: str = '', reference_id: str = '') -> Transaction:
        """Withdraw funds from a wallet"""
        try:
            wallet = self.get_wallet(wallet_id)
            if not wallet:
                raise ValueError(f"Wallet {wallet_id} not found")
            
            if isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            
            if amount <= 0:
                raise ValueError("Withdrawal amount must be positive")
            
            if wallet.balance < amount:
                raise ValueError("Insufficient funds")
            
            # Create transaction
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                id=transaction_id,
                wallet_id=wallet_id,
                amount=amount,
                currency=wallet.currency,
                type='withdrawal',
                status='completed',
                description=description,
                reference_id=reference_id
            )
            
            # Update wallet balance
            wallet.balance -= amount
            wallet.updated_at = datetime.utcnow()
            
            # Store transaction
            self.transactions[transaction_id] = transaction
            
            logger.info(f"Withdrew {amount} {wallet.currency} from wallet {wallet_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to withdraw from wallet {wallet_id}: {e}")
            raise
    
    def transfer(self, from_wallet_id: str, to_wallet_id: str, 
                 amount: Union[Decimal, float, int], description: str = '') -> List[Transaction]:
        """Transfer funds between wallets"""
        try:
            from_wallet = self.get_wallet(from_wallet_id)
            to_wallet = self.get_wallet(to_wallet_id)
            
            if not from_wallet:
                raise ValueError(f"Source wallet {from_wallet_id} not found")
            if not to_wallet:
                raise ValueError(f"Destination wallet {to_wallet_id} not found")
            
            if from_wallet.currency != to_wallet.currency:
                raise ValueError("Wallets must use the same currency")
            
            if isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            
            if amount <= 0:
                raise ValueError("Transfer amount must be positive")
            
            if from_wallet.balance < amount:
                raise ValueError("Insufficient funds in source wallet")
            
            transactions = []
            
            # Create withdrawal transaction
            withdraw_id = str(uuid.uuid4())
            withdraw_transaction = Transaction(
                id=withdraw_id,
                wallet_id=from_wallet_id,
                amount=amount,
                currency=from_wallet.currency,
                type='transfer',
                status='completed',
                description=f"Transfer to {to_wallet_id}: {description}",
                reference_id=to_wallet_id
            )
            transactions.append(withdraw_transaction)
            
            # Create deposit transaction
            deposit_id = str(uuid.uuid4())
            deposit_transaction = Transaction(
                id=deposit_id,
                wallet_id=to_wallet_id,
                amount=amount,
                currency=to_wallet.currency,
                type='transfer',
                status='completed',
                description=f"Transfer from {from_wallet_id}: {description}",
                reference_id=from_wallet_id
            )
            transactions.append(deposit_transaction)
            
            # Update wallet balances
            from_wallet.balance -= amount
            from_wallet.updated_at = datetime.utcnow()
            
            to_wallet.balance += amount
            to_wallet.updated_at = datetime.utcnow()
            
            # Store transactions
            self.transactions[withdraw_id] = withdraw_transaction
            self.transactions[deposit_id] = deposit_transaction
            
            logger.info(f"Transferred {amount} {from_wallet.currency} from wallet {from_wallet_id} to {to_wallet_id}")
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to transfer funds: {e}")
            raise
    
    def get_wallet_transactions(self, wallet_id: str, limit: int = 50) -> List[Transaction]:
        """Get transactions for a wallet"""
        transactions = [
            tx for tx in self.transactions.values() 
            if tx.wallet_id == wallet_id
        ]
        # Sort by creation date, newest first
        transactions.sort(key=lambda x: x.created_at, reverse=True)
        return transactions[:limit]
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.transactions.get(transaction_id)


class ReferralManager:
    """Main referral management service"""
    
    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager
        self.referrals: Dict[str, Referral] = {}
        self.referral_programs: Dict[str, ReferralProgram] = wallet_manager.referral_programs
    
    def create_referral(self, referrer_id: str, referee_id: str, 
                       program_id: str = 'default') -> Referral:
        """Create a new referral"""
        try:
            if referrer_id == referee_id:
                raise ValueError("User cannot refer themselves")
            
            program = self.referral_programs.get(program_id)
            if not program or not program.is_active:
                raise ValueError(f"Referral program {program_id} not found or inactive")
            
            # Check if referrer already has too many referrals
            existing_referrals = [
                r for r in self.referrals.values() 
                if r.referrer_id == referrer_id and r.status != 'expired'
            ]
            if len(existing_referrals) >= program.max_referrals_per_user:
                raise ValueError("Maximum referrals per user exceeded")
            
            # Create referral
            referral_id = str(uuid.uuid4())
            referral = Referral(
                id=referral_id,
                referrer_id=referrer_id,
                referee_id=referee_id,
                reward_amount=program.reward_amount,
                currency=program.currency,
                expired_at=datetime.utcnow() + timedelta(days=program.expiration_days)
            )
            
            self.referrals[referral_id] = referral
            logger.info(f"Created referral {referral_id} from {referrer_id} to {referee_id}")
            return referral
            
        except Exception as e:
            logger.error(f"Failed to create referral: {e}")
            raise
    
    def get_referral_by_code(self, referral_code: str) -> Optional[Referral]:
        """Get referral by referral code"""
        for referral in self.referrals.values():
            if referral.referral_code == referral_code:
                return referral
        return None
    
    def get_user_referrals(self, user_id: str) -> List[Referral]:
        """Get all referrals for a user (as referrer)"""
        return [
            r for r in self.referrals.values() 
            if r.referrer_id == user_id
        ]
    
    def get_referral(self, referral_id: str) -> Optional[Referral]:
        """Get referral by ID"""
        return self.referrals.get(referral_id)
    
    def mark_referral_converted(self, referral_id: str, 
                               purchase_amount: Union[Decimal, float, int] = None) -> bool:
        """Mark a referral as converted (successful)"""
        try:
            referral = self.get_referral(referral_id)
            if not referral:
                raise ValueError(f"Referral {referral_id} not found")
            
            if referral.status != 'pending':
                raise ValueError(f"Referral {referral_id} is not pending")
            
            program = self.referral_programs.get('default')
            if not program:
                raise ValueError("Default referral program not found")
            
            # Check minimum purchase requirement
            if purchase_amount is not None:
                if isinstance(purchase_amount, (int, float)):
                    purchase_amount = Decimal(str(purchase_amount))
                
                if purchase_amount < program.minimum_purchase:
                    raise ValueError(f"Purchase amount {purchase_amount} below minimum {program.minimum_purchase}")
            
            # Mark as converted
            referral.status = 'converted'
            referral.converted_at = datetime.utcnow()
            
            # Award rewards to both users
            self._award_referral_rewards(referral, program)
            
            logger.info(f"Marked referral {referral_id} as converted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark referral {referral_id} as converted: {e}")
            raise
    
    def _award_referral_rewards(self, referral: Referral, program: ReferralProgram):
        """Award rewards to referrer and referee"""
        try:
            # Award to referrer
            referrer_wallet = self.wallet_manager.get_user_wallet(referral.referrer_id, referral.currency)
            if not referrer_wallet:
                referrer_wallet = self.wallet_manager.create_wallet(referral.referrer_id, referral.currency)
            
            self.wallet_manager.deposit(
                referrer_wallet.id,
                referral.reward_amount,
                f"Referral reward for {referral.referee_id}",
                referral.id
            )
            
            # Award to referee (if program allows)
            # For this demo, we'll award the same amount to the referee
            referee_wallet = self.wallet_manager.get_user_wallet(referral.referee_id, referral.currency)
            if not referee_wallet:
                referee_wallet = self.wallet_manager.create_wallet(referral.referee_id, referral.currency)
            
            self.wallet_manager.deposit(
                referee_wallet.id,
                referral.reward_amount,
                f"Referral bonus for being referred by {referral.referrer_id}",
                referral.id
            )
            
            logger.info(f"Awarded referral rewards for referral {referral.id}")
            
        except Exception as e:
            logger.error(f"Failed to award referral rewards: {e}")
            raise
    
    def expire_old_referrals(self):
        """Expire referrals that have passed their expiration date"""
        try:
            now = datetime.utcnow()
            expired_count = 0
            
            for referral in self.referrals.values():
                if referral.status == 'pending' and referral.expired_at and referral.expired_at < now:
                    referral.status = 'expired'
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Expired {expired_count} old referrals")
            
        except Exception as e:
            logger.error(f"Failed to expire old referrals: {e}")
    
    def get_program(self, program_id: str = 'default') -> Optional[ReferralProgram]:
        """Get referral program by ID"""
        return self.referral_programs.get(program_id)
    
    def create_program(self, program: ReferralProgram) -> bool:
        """Create a new referral program"""
        try:
            self.referral_programs[program.id] = program
            logger.info(f"Created referral program {program.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create referral program {program.id}: {e}")
            return False


# Utility functions for wallet and referral management

def format_currency(amount: Union[Decimal, float, int], currency: str = 'USD') -> str:
    """Format amount as currency string"""
    if isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'CA$',
        'BTC': '₿',
        'ETH': 'Ξ'
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def validate_wallet_id(wallet_id: str) -> bool:
    """Validate wallet ID format"""
    try:
        uuid.UUID(wallet_id)
        return True
    except ValueError:
        return False


def validate_amount(amount: Union[Decimal, float, int]) -> bool:
    """Validate amount is positive"""
    if isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    return amount > 0


def generate_referral_link(referral_code: str, base_url: str = "https://example.com") -> str:
    """Generate referral link"""
    return f"{base_url}/referral/{referral_code}"


# Example usage and testing functions

def demo_wallet_operations():
    """Demonstrate wallet operations"""
    print("=== Wallet Operations Demo ===")
    
    # Initialize managers
    wallet_manager = WalletManager()
    referral_manager = ReferralManager(wallet_manager)
    
    # Create wallets
    user1_wallet = wallet_manager.create_wallet("user1", "USD")
    user2_wallet = wallet_manager.create_wallet("user2", "USD")
    
    print(f"Created wallets: {user1_wallet.id}, {user2_wallet.id}")
    
    # Deposit funds
    deposit1 = wallet_manager.deposit(user1_wallet.id, 100.00, "Initial deposit")
    deposit2 = wallet_manager.deposit(user2_wallet.id, 50.00, "Initial deposit")
    
    print(f"Deposited funds: {deposit1.amount}, {deposit2.amount}")
    
    # Check balances
    print(f"User1 balance: {format_currency(user1_wallet.balance, user1_wallet.currency)}")
    print(f"User2 balance: {format_currency(user2_wallet.balance, user2_wallet.currency)}")
    
    # Transfer funds
    transfers = wallet_manager.transfer(user1_wallet.id, user2_wallet.id, 25.00, "Friend payment")
    print(f"Transferred funds: {len(transfers)} transactions")
    
    # Check updated balances
    print(f"User1 balance: {format_currency(user1_wallet.balance, user1_wallet.currency)}")
    print(f"User2 balance: {format_currency(user2_wallet.balance, user2_wallet.currency)}")
    
    # Create referral
    referral = referral_manager.create_referral("user1", "user3")
    print(f"Created referral: {referral.id} with code {referral.referral_code}")
    
    # Generate referral link
    referral_link = generate_referral_link(referral.referral_code)
    print(f"Referral link: {referral_link}")
    
    # Mark referral as converted
    referral_manager.mark_referral_converted(referral.id, 50.00)
    print(f"Marked referral as converted")
    
    # Check updated balances after referral rewards
    user1_wallet = wallet_manager.get_wallet(user1_wallet.id)
    user2_wallet = wallet_manager.get_wallet(user2_wallet.id)
    print(f"User1 balance: {format_currency(user1_wallet.balance, user1_wallet.currency)}")
    print(f"User2 balance: {format_currency(user2_wallet.balance, user2_wallet.currency)}")


if __name__ == "__main__":
    demo_wallet_operations()