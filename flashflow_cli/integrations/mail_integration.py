"""
Mail Integration Layer for FlashFlow
===================================

Integration layer for mail services with React components and Flask routes.
"""

import os
import json
from typing import Dict, List, Any, Optional
from ..services.mail_integration import MailIntegrationManager

class MailIntegrationLayer:
    """Integration layer for mail services in FlashFlow"""
    
    def __init__(self):
        self.mail_manager = MailIntegrationManager()
    
    def generate_mail_components(self, project_path: str, mail_config: Dict) -> Dict[str, str]:
        """Generate React components for mail services"""
        components = {}
        
        # Email composer component
        components['EmailComposer'] = self._generate_email_composer()
        
        # Email list/inbox component
        components['EmailInbox'] = self._generate_email_inbox()
        
        # Mail provider settings component
        components['MailSettings'] = self._generate_mail_settings()
        
        # Email template manager
        components['EmailTemplates'] = self._generate_email_templates()
        
        return components
    
    def _generate_email_composer(self) -> str:
        """Generate email composer component"""
        return '''import React, { useState } from 'react';

export const EmailComposer = ({ onSend, providers = [] }) => {
  const [email, setEmail] = useState({
    to: '',
    cc: '',
    bcc: '',
    subject: '',
    text_content: '',
    html_content: '',
    provider: providers[0] || 'smtp'
  });
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);
    
    try {
      const response = await fetch('/api/mail/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(email)
      });
      
      const result = await response.json();
      
      if (result.success) {
        onSend?.(result);
        setEmail({ ...email, to: '', subject: '', text_content: '', html_content: '' });
      } else {
        alert('Failed to send email: ' + result.error);
      }
    } catch (error) {
      alert('Error sending email: ' + error.message);
    }
    
    setSending(false);
  };

  return (
    <div className="email-composer">
      <h3>Compose Email</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Provider:</label>
          <select 
            value={email.provider} 
            onChange={(e) => setEmail({...email, provider: e.target.value})}
          >
            {providers.map(provider => (
              <option key={provider} value={provider}>{provider}</option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label>To:</label>
          <input
            type="email"
            value={email.to}
            onChange={(e) => setEmail({...email, to: e.target.value})}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Subject:</label>
          <input
            type="text"
            value={email.subject}
            onChange={(e) => setEmail({...email, subject: e.target.value})}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Message:</label>
          <textarea
            value={email.text_content}
            onChange={(e) => setEmail({...email, text_content: e.target.value})}
            rows={10}
            required
          />
        </div>
        
        <button type="submit" disabled={sending}>
          {sending ? 'Sending...' : 'Send Email'}
        </button>
      </form>
    </div>
  );
};'''

    def _generate_email_inbox(self) -> str:
        """Generate email inbox component"""
        return '''import React, { useState, useEffect } from 'react';

export const EmailInbox = ({ folder = 'INBOX' }) => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);

  useEffect(() => {
    loadEmails();
  }, [folder]);

  const loadEmails = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/mail/emails?folder=${folder}&limit=20`);
      const result = await response.json();
      
      if (result.success) {
        setEmails(result.emails);
      } else {
        console.error('Failed to load emails:', result.error);
      }
    } catch (error) {
      console.error('Error loading emails:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return <div>Loading emails...</div>;
  }

  return (
    <div className="email-inbox">
      <h3>Inbox - {folder}</h3>
      
      <div className="email-list">
        {emails.map(email => (
          <div 
            key={email.id} 
            className={`email-item ${selectedEmail?.id === email.id ? 'selected' : ''}`}
            onClick={() => setSelectedEmail(email)}
          >
            <div className="email-from">{email.from}</div>
            <div className="email-subject">{email.subject}</div>
            <div className="email-date">{new Date(email.date).toLocaleDateString()}</div>
          </div>
        ))}
      </div>

      {selectedEmail && (
        <div className="email-content">
          <h4>{selectedEmail.subject}</h4>
          <p><strong>From:</strong> {selectedEmail.from}</p>
          <p><strong>To:</strong> {selectedEmail.to}</p>
          <p><strong>Date:</strong> {selectedEmail.date}</p>
          <div className="email-body">
            {selectedEmail.html_content ? (
              <div dangerouslySetInnerHTML={{ __html: selectedEmail.html_content }} />
            ) : (
              <pre>{selectedEmail.text_content}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
};'''

    def _generate_mail_settings(self) -> str:
        """Generate mail settings component"""
        return '''import React, { useState, useEffect } from 'react';

export const MailSettings = () => {
  const [providers, setProviders] = useState({});
  const [activeProvider, setActiveProvider] = useState('');
  const [config, setConfig] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await fetch('/api/mail/status');
      const result = await response.json();
      
      if (result.success) {
        setProviders(result.status);
        setActiveProvider(result.status.default_provider || '');
      }
    } catch (error) {
      console.error('Error loading mail status:', error);
    }
  };

  const saveProvider = async (provider) => {
    setSaving(true);
    try {
      const response = await fetch(`/api/mail/configure/${provider}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert('Provider configured successfully');
        loadStatus();
      } else {
        alert('Configuration failed: ' + result.error);
      }
    } catch (error) {
      alert('Error configuring provider: ' + error.message);
    }
    setSaving(false);
  };

  return (
    <div className="mail-settings">
      <h3>Mail Provider Settings</h3>
      
      <div className="provider-status">
        <h4>Current Status</h4>
        <p>Default Provider: {providers.default_provider || 'None'}</p>
        <p>Active Providers: {providers.active_providers?.join(', ') || 'None'}</p>
      </div>

      <div className="provider-config">
        <h4>Configure Provider</h4>
        <select 
          value={activeProvider} 
          onChange={(e) => setActiveProvider(e.target.value)}
        >
          <option value="">Select Provider</option>
          <option value="smtp">SMTP</option>
          <option value="sendgrid">SendGrid</option>
          <option value="mailgun">Mailgun</option>
          <option value="ses">Amazon SES</option>
        </select>

        {activeProvider === 'smtp' && (
          <div className="smtp-config">
            <input
              placeholder="SMTP Host"
              value={config.host || ''}
              onChange={(e) => setConfig({...config, host: e.target.value})}
            />
            <input
              placeholder="Port"
              type="number"
              value={config.port || ''}
              onChange={(e) => setConfig({...config, port: e.target.value})}
            />
            <input
              placeholder="Username"
              value={config.username || ''}
              onChange={(e) => setConfig({...config, username: e.target.value})}
            />
            <input
              placeholder="Password"
              type="password"
              value={config.password || ''}
              onChange={(e) => setConfig({...config, password: e.target.value})}
            />
          </div>
        )}

        {activeProvider === 'sendgrid' && (
          <div className="sendgrid-config">
            <input
              placeholder="SendGrid API Key"
              type="password"
              value={config.api_key || ''}
              onChange={(e) => setConfig({...config, api_key: e.target.value})}
            />
          </div>
        )}

        <button onClick={() => saveProvider(activeProvider)} disabled={saving}>
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
};'''

    def _generate_email_templates(self) -> str:
        """Generate email templates component"""
        return '''import React, { useState } from 'react';

export const EmailTemplates = ({ onUseTemplate }) => {
  const [templates] = useState([
    {
      name: 'Welcome Email',
      subject: 'Welcome to {{app_name}}!',
      content: 'Hello {{name}},\\n\\nWelcome to our platform!\\n\\nBest regards,\\nThe Team'
    },
    {
      name: 'Password Reset',
      subject: 'Password Reset Request',
      content: 'Hello {{name}},\\n\\nClick the link below to reset your password:\\n{{reset_link}}\\n\\nIf you did not request this, please ignore this email.'
    },
    {
      name: 'Invoice',
      subject: 'Invoice #{{invoice_number}}',
      content: 'Dear {{name}},\\n\\nPlease find your invoice attached.\\n\\nAmount: {{amount}}\\nDue Date: {{due_date}}\\n\\nThank you!'
    }
  ]);

  return (
    <div className="email-templates">
      <h3>Email Templates</h3>
      
      <div className="template-list">
        {templates.map((template, index) => (
          <div key={index} className="template-item">
            <h4>{template.name}</h4>
            <p><strong>Subject:</strong> {template.subject}</p>
            <p><strong>Content:</strong></p>
            <pre>{template.content}</pre>
            <button onClick={() => onUseTemplate?.(template)}>
              Use Template
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};'''

    def generate_flask_routes(self, mail_config: Dict) -> str:
        """Generate Flask routes for mail services"""
        return '''from flask import Blueprint, request, jsonify
from ..services.mail_integration import MailIntegrationManager

mail_bp = Blueprint('mail', __name__, url_prefix='/api/mail')
mail_manager = MailIntegrationManager()

@mail_bp.route('/configure/<provider>', methods=['POST'])
def configure_provider(provider):
    """Configure mail provider"""
    try:
        config = request.json
        result = mail_manager.initialize_provider(provider, config)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@mail_bp.route('/status', methods=['GET'])
def get_status():
    """Get mail provider status"""
    try:
        status = mail_manager.get_provider_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@mail_bp.route('/send', methods=['POST'])
def send_email():
    """Send email"""
    try:
        email_data = request.json
        provider = email_data.pop('provider', None)
        result = mail_manager.send_email(email_data, provider)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@mail_bp.route('/emails', methods=['GET'])
def get_emails():
    """Get emails from inbox"""
    try:
        folder = request.args.get('folder', 'INBOX')
        limit = int(request.args.get('limit', 10))
        result = mail_manager.get_emails(folder, limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})'''

    def create_demo_flow(self, project_path: str) -> str:
        """Create demo .flow file for mail integration"""
        return '''# Mail Integration Demo
app "Mail Demo" {
    title: "Mail Integration Demo"
    description: "Demonstrating FlashFlow mail capabilities"
    
    # Mail configuration
    mail_config {
        providers: {
            smtp: {
                host: "smtp.gmail.com"
                port: 587
                use_tls: true
            }
            sendgrid: {
                api_key: "your-sendgrid-api-key"
            }
            mailgun: {
                api_key: "your-mailgun-api-key"
                domain: "your-domain.com"
            }
        }
        
        default_provider: "smtp"
        from_email: "noreply@example.com"
        from_name: "FlashFlow App"
    }
}

# Email composer page
page email_compose {
    title: "Compose Email"
    
    component EmailComposer {
        providers: ["smtp", "sendgrid", "mailgun"]
        
        events: {
            onSend: handle_email_sent
        }
        
        templates: {
            welcome: "Welcome Email Template"
            notification: "Notification Template"
            invoice: "Invoice Template"
        }
    }
    
    component EmailTemplates {
        on_use_template: load_template
    }
}

# Email inbox page
page email_inbox {
    title: "Email Inbox"
    
    component EmailInbox {
        folder: "INBOX"
        auto_refresh: 30  # seconds
        
        events: {
            onEmailSelect: handle_email_select
            onRefresh: refresh_emails
        }
    }
    
    component MailSettings {
        allow_provider_switch: true
        
        events: {
            onProviderChange: handle_provider_change
        }
    }
}

# Mail API routes
api mail_api {
    base_path: "/api/mail"
    
    endpoints: {
        "POST /configure/:provider": configure_mail_provider
        "GET /status": get_mail_status
        "POST /send": send_email
        "GET /emails": get_inbox_emails
        "POST /templates": save_email_template
        "GET /templates": get_email_templates
    }
}

# Event handlers
handlers {
    handle_email_sent(result) {
        if (result.success) {
            log("Email sent successfully: " + result.message_id)
            show_notification("Email sent!", "success")
            
            # Save to sent items
            save_sent_email(result)
        } else {
            log("Email send failed: " + result.error)
            show_notification("Failed to send email", "error")
        }
    }
    
    handle_email_select(email) {
        log("Email selected: " + email.subject)
        
        # Mark as read
        mark_email_read(email.id)
        
        # Update UI
        display_email_content(email)
    }
    
    handle_provider_change(provider) {
        log("Mail provider changed to: " + provider)
        
        # Update default provider
        set_default_mail_provider(provider)
        
        # Refresh provider status
        refresh_mail_status()
    }
}

# Background jobs
jobs {
    # Check for new emails
    check_new_emails {
        schedule: "*/5 * * * *"  # Every 5 minutes
        
        task() {
            if (mail_config.imap_enabled) {
                new_emails = fetch_new_emails()
                
                if (new_emails.length > 0) {
                    log("Found " + new_emails.length + " new emails")
                    
                    # Send notifications
                    for email in new_emails {
                        send_push_notification({
                            title: "New Email",
                            body: email.subject,
                            data: { email_id: email.id }
                        })
                    }
                }
            }
        }
    }
    
    # Clean up old sent emails
    cleanup_sent_emails {
        schedule: "0 2 * * 0"  # Weekly at 2 AM Sunday
        
        task() {
            cutoff_date = date_subtract(now(), days: 30)
            
            old_emails = query_sent_emails(sent_before: cutoff_date)
            
            for email in old_emails {
                delete_sent_email(email.id)
            }
            
            log("Cleaned up " + old_emails.length + " old sent emails")
        }
    }
}'''