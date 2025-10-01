"""
FlashFlow Mail Integration Service
=================================

Comprehensive mail server integration with multiple providers.
"""

import smtplib
import imaplib
import email
import json
import requests
import base64
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class MailIntegrationManager:
    """Unified manager for mail integration services"""
    
    def __init__(self):
        self.smtp_service = SMTPService()
        self.imap_service = IMAPService() 
        self.sendgrid_service = SendGridService()
        self.mailgun_service = MailgunService()
        self.ses_service = AmazonSESService()
        self.active_providers = {}
        self.default_provider = None
    
    def initialize_provider(self, provider: str, config: Dict) -> Dict:
        """Initialize mail provider with configuration"""
        try:
            if provider == 'smtp':
                result = self.smtp_service.configure(config)
            elif provider == 'imap':
                result = self.imap_service.configure(config)
            elif provider == 'sendgrid':
                result = self.sendgrid_service.configure(config)
            elif provider == 'mailgun':
                result = self.mailgun_service.configure(config)
            elif provider == 'ses':
                result = self.ses_service.configure(config)
            else:
                return {'success': False, 'error': f'Unsupported provider: {provider}'}
            
            if result['success']:
                self.active_providers[provider] = config
                if not self.default_provider:
                    self.default_provider = provider
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email(self, email_data: Dict, provider: str = None) -> Dict:
        """Send email using specified or default provider"""
        try:
            provider = provider or self.default_provider
            
            if not provider or provider not in self.active_providers:
                return {'success': False, 'error': 'No active mail provider configured'}
            
            if provider == 'smtp':
                return self.smtp_service.send_email(email_data)
            elif provider == 'sendgrid':
                return self.sendgrid_service.send_email(email_data)
            elif provider == 'mailgun':
                return self.mailgun_service.send_email(email_data)
            elif provider == 'ses':
                return self.ses_service.send_email(email_data)
            else:
                return {'success': False, 'error': f'Provider {provider} not supported for sending'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_emails(self, folder: str = 'INBOX', limit: int = 10) -> Dict:
        """Get emails using IMAP"""
        if 'imap' not in self.active_providers:
            return {'success': False, 'error': 'IMAP not configured'}
        
        return self.imap_service.get_emails(folder, limit)
    
    def get_provider_status(self) -> Dict:
        """Get status of all mail providers"""
        return {
            'active_providers': list(self.active_providers.keys()),
            'default_provider': self.default_provider,
            'smtp_configured': bool(self.smtp_service.host),
            'imap_configured': bool(self.imap_service.host),
            'sendgrid_configured': bool(self.sendgrid_service.api_key),
            'mailgun_configured': bool(self.mailgun_service.api_key),
            'ses_configured': bool(self.ses_service.access_key_id)
        }


class SMTPService:
    """SMTP email service for sending emails"""
    
    def __init__(self):
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.use_tls = True
    
    def configure(self, config: Dict) -> Dict:
        """Configure SMTP settings"""
        try:
            self.host = config['host']
            self.port = config.get('port', 587)
            self.username = config['username']
            self.password = config['password']
            self.use_tls = config.get('use_tls', True)
            
            # Test connection
            test_result = self._test_connection()
            
            if test_result['success']:
                return {
                    'success': True,
                    'message': 'SMTP configured successfully',
                    'host': self.host,
                    'port': self.port
                }
            else:
                return {'success': False, 'error': test_result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_connection(self) -> Dict:
        """Test SMTP connection"""
        try:
            server = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.quit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email(self, email_data: Dict) -> Dict:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = email_data.get('from_email', self.username)
            msg['To'] = ', '.join(email_data['to']) if isinstance(email_data['to'], list) else email_data['to']
            msg['Subject'] = email_data['subject']
            
            # Add content
            if email_data.get('text_content'):
                msg.attach(MIMEText(email_data['text_content'], 'plain'))
            
            if email_data.get('html_content'):
                msg.attach(MIMEText(email_data['html_content'], 'html'))
            
            # Send email
            server = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            
            recipients = email_data['to'] if isinstance(email_data['to'], list) else [email_data['to']]
            server.send_message(msg, to_addrs=recipients)
            server.quit()
            
            return {
                'success': True,
                'message_id': msg['Message-ID'],
                'recipients': len(recipients)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class IMAPService:
    """IMAP service for reading emails"""
    
    def __init__(self):
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.use_ssl = True
        self.connection = None
    
    def configure(self, config: Dict) -> Dict:
        """Configure IMAP settings"""
        try:
            self.host = config['host']
            self.port = config.get('port', 993)
            self.username = config['username']
            self.password = config['password']
            self.use_ssl = config.get('use_ssl', True)
            
            # Test connection
            test_result = self._test_connection()
            
            if test_result['success']:
                return {
                    'success': True,
                    'message': 'IMAP configured successfully',
                    'host': self.host
                }
            else:
                return {'success': False, 'error': test_result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_connection(self) -> Dict:
        """Test IMAP connection"""
        try:
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                mail = imaplib.IMAP4(self.host, self.port)
            
            mail.login(self.username, self.password)
            mail.logout()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_emails(self, folder: str = 'INBOX', limit: int = 10) -> Dict:
        """Get emails from specified folder"""
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                self.connection = imaplib.IMAP4(self.host, self.port)
            
            self.connection.login(self.username, self.password)
            self.connection.select(folder)
            
            # Search for emails
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                return {'success': False, 'error': 'Failed to search emails'}
            
            email_ids = messages[0].split()
            emails = []
            
            # Get latest emails
            for email_id in email_ids[-limit:]:
                email_data = self._parse_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            self.connection.logout()
            
            return {
                'success': True,
                'emails': emails,
                'total_count': len(email_ids),
                'folder': folder
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_email(self, email_id: bytes) -> Optional[Dict]:
        """Parse email data"""
        try:
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            email_message = email.message_from_bytes(msg_data[0][1])
            
            # Get content
            text_content = ''
            html_content = ''
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        text_content = part.get_payload(decode=True).decode()
                    elif content_type == 'text/html':
                        html_content = part.get_payload(decode=True).decode()
            else:
                text_content = email_message.get_payload(decode=True).decode()
            
            return {
                'id': email_id.decode(),
                'subject': email_message['Subject'],
                'from': email_message['From'],
                'to': email_message['To'],
                'date': email_message['Date'],
                'text_content': text_content,
                'html_content': html_content
            }
            
        except Exception as e:
            return None


class SendGridService:
    """SendGrid API email service"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.sendgrid.com/v3"
    
    def configure(self, config: Dict) -> Dict:
        """Configure SendGrid settings"""
        try:
            self.api_key = config['api_key']
            
            # Test API key
            test_result = self._test_api_key()
            
            if test_result['success']:
                return {
                    'success': True,
                    'message': 'SendGrid configured successfully'
                }
            else:
                return {'success': False, 'error': test_result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_api_key(self) -> Dict:
        """Test SendGrid API key"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/user/profile", headers=headers)
            
            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'error': f'API key validation failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email(self, email_data: Dict) -> Dict:
        """Send email via SendGrid API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Prepare recipients
            to_list = []
            if isinstance(email_data['to'], list):
                for recipient in email_data['to']:
                    to_list.append({'email': recipient})
            else:
                to_list.append({'email': email_data['to']})
            
            # Prepare email payload
            payload = {
                'personalizations': [{
                    'to': to_list,
                    'subject': email_data['subject']
                }],
                'from': {
                    'email': email_data.get('from_email', 'noreply@example.com')
                },
                'content': []
            }
            
            # Add content
            if email_data.get('text_content'):
                payload['content'].append({
                    'type': 'text/plain',
                    'value': email_data['text_content']
                })
            
            if email_data.get('html_content'):
                payload['content'].append({
                    'type': 'text/html',
                    'value': email_data['html_content']
                })
            
            response = requests.post(f"{self.base_url}/mail/send", headers=headers, json=payload)
            
            if response.status_code == 202:
                return {
                    'success': True,
                    'message_id': response.headers.get('X-Message-Id'),
                    'provider': 'sendgrid'
                }
            else:
                return {
                    'success': False,
                    'error': f'SendGrid API error: {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MailgunService:
    """Mailgun API email service"""
    
    def __init__(self):
        self.api_key = None
        self.domain = None
        self.base_url = "https://api.mailgun.net/v3"
    
    def configure(self, config: Dict) -> Dict:
        """Configure Mailgun settings"""
        try:
            self.api_key = config['api_key']
            self.domain = config['domain']
            
            # Test API key
            test_result = self._test_api_key()
            
            if test_result['success']:
                return {
                    'success': True,
                    'message': 'Mailgun configured successfully',
                    'domain': self.domain
                }
            else:
                return {'success': False, 'error': test_result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_api_key(self) -> Dict:
        """Test Mailgun API key"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.domain}",
                auth=("api", self.api_key)
            )
            
            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'error': f'API key validation failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email(self, email_data: Dict) -> Dict:
        """Send email via Mailgun API"""
        try:
            # Prepare email data
            data = {
                'from': email_data.get('from_email', f'noreply@{self.domain}'),
                'to': email_data['to'] if isinstance(email_data['to'], str) else ', '.join(email_data['to']),
                'subject': email_data['subject']
            }
            
            # Add content
            if email_data.get('text_content'):
                data['text'] = email_data['text_content']
            
            if email_data.get('html_content'):
                data['html'] = email_data['html_content']
            
            response = requests.post(
                f"{self.base_url}/{self.domain}/messages",
                auth=("api", self.api_key),
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'message_id': result.get('id'),
                    'provider': 'mailgun'
                }
            else:
                return {
                    'success': False,
                    'error': f'Mailgun API error: {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AmazonSESService:
    """Amazon Simple Email Service (SES) integration"""
    
    def __init__(self):
        self.access_key_id = None
        self.secret_access_key = None
        self.region = None
    
    def configure(self, config: Dict) -> Dict:
        """Configure AWS SES settings"""
        try:
            self.access_key_id = config['access_key_id']
            self.secret_access_key = config['secret_access_key']
            self.region = config.get('region', 'us-east-1')
            
            # Test SES connection
            test_result = self._test_connection()
            
            if test_result['success']:
                return {
                    'success': True,
                    'message': 'AWS SES configured successfully',
                    'region': self.region
                }
            else:
                return {'success': False, 'error': test_result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_connection(self) -> Dict:
        """Test AWS SES connection"""
        try:
            import boto3
            
            client = boto3.client(
                'ses',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            )
            
            # Test by getting send quota
            response = client.get_send_quota()
            return {'success': True}
            
        except ImportError:
            return {'success': False, 'error': 'boto3 not installed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_email(self, email_data: Dict) -> Dict:
        """Send email via AWS SES"""
        try:
            import boto3
            
            client = boto3.client(
                'ses',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            )
            
            # Prepare destinations
            destinations = {
                'ToAddresses': email_data['to'] if isinstance(email_data['to'], list) else [email_data['to']]
            }
            
            # Prepare message
            message = {
                'Subject': {'Data': email_data['subject']},
                'Body': {}
            }
            
            if email_data.get('text_content'):
                message['Body']['Text'] = {'Data': email_data['text_content']}
            
            if email_data.get('html_content'):
                message['Body']['Html'] = {'Data': email_data['html_content']}
            
            response = client.send_email(
                Source=email_data.get('from_email', 'noreply@example.com'),
                Destination=destinations,
                Message=message
            )
            
            return {
                'success': True,
                'message_id': response['MessageId'],
                'provider': 'ses'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}