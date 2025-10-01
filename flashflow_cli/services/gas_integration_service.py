"""
FlashFlow Google Apps Script Integration Service
Provides Google Apps Script automation and Google Workspace integration
"""

import json
import os
import tempfile
import requests
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import base64
from datetime import datetime

class GoogleAppsScriptService:
    """Google Apps Script integration service"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.credentials = None
        self.script_api_base = "https://script.googleapis.com/v1"
        self.drive_api_base = "https://www.googleapis.com/drive/v3"
        self.sheets_api_base = "https://sheets.googleapis.com/v4"
        self.docs_api_base = "https://docs.googleapis.com/v1"
        self.access_token = None
    
    def setup_credentials(self, credentials_config: Dict) -> bool:
        """Setup Google API credentials"""
        try:
            if 'service_account_file' in credentials_config:
                # Service account authentication
                self.credentials = self._setup_service_account(credentials_config['service_account_file'])
            elif 'oauth_credentials' in credentials_config:
                # OAuth 2.0 authentication
                self.credentials = self._setup_oauth(credentials_config['oauth_credentials'])
            else:
                return False
            
            return self.credentials is not None
        except Exception as e:
            print(f"Failed to setup credentials: {e}")
            return False
    
    def _setup_service_account(self, service_account_file: str) -> Dict:
        """Setup service account credentials"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
            
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=[
                    'https://www.googleapis.com/auth/script.projects',
                    'https://www.googleapis.com/auth/script.deployments',
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/documents'
                ]
            )
            
            credentials.refresh(Request())
            self.access_token = credentials.token
            
            return {
                'type': 'service_account',
                'credentials': credentials,
                'token': credentials.token
            }
        except ImportError:
            print("Google Auth libraries not installed. Install: pip install google-auth google-auth-oauthlib")
            return None
        except Exception as e:
            print(f"Service account setup failed: {e}")
            return None
    
    def _setup_oauth(self, oauth_config: Dict) -> Dict:
        """Setup OAuth 2.0 credentials"""
        try:
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import Flow
            
            # OAuth flow setup
            flow = Flow.from_client_config(
                oauth_config,
                scopes=[
                    'https://www.googleapis.com/auth/script.projects',
                    'https://www.googleapis.com/auth/script.deployments',
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/documents'
                ]
            )
            
            return {
                'type': 'oauth',
                'flow': flow,
                'token': None
            }
        except ImportError:
            print("Google Auth libraries not installed")
            return None
        except Exception as e:
            print(f"OAuth setup failed: {e}")
            return None
    
    def create_script_project(self, project_name: str, script_code: str) -> Dict:
        """Create a new Google Apps Script project"""
        if not self.access_token:
            return {'success': False, 'error': 'No authentication token'}
        
        try:
            # Create the script project
            create_payload = {
                'title': project_name,
                'parentId': self.config.get('parent_folder_id')
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.script_api_base}/projects",
                headers=headers,
                json=create_payload
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Failed to create project: {response.text}'
                }
            
            project_data = response.json()
            script_id = project_data['scriptId']
            
            # Update the script content
            update_result = self.update_script_content(script_id, script_code)
            
            if update_result['success']:
                return {
                    'success': True,
                    'script_id': script_id,
                    'project_data': project_data,
                    'web_app_url': None
                }
            else:
                return update_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Script creation failed: {e}'
            }
    
    def update_script_content(self, script_id: str, script_code: str, file_name: str = "Code.gs") -> Dict:
        """Update the content of a Google Apps Script project"""
        if not self.access_token:
            return {'success': False, 'error': 'No authentication token'}
        
        try:
            # Get current project content
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Update the script files
            update_payload = {
                'files': [
                    {
                        'name': file_name,
                        'type': 'SERVER_JS',
                        'source': script_code
                    }
                ]
            }
            
            response = requests.put(
                f"{self.script_api_base}/projects/{script_id}/content",
                headers=headers,
                json=update_payload
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'script_id': script_id,
                    'updated_files': [file_name]
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to update script: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Script update failed: {e}'
            }
    
    def deploy_web_app(self, script_id: str, description: str = "FlashFlow Auto Deployment") -> Dict:
        """Deploy Google Apps Script as a web app"""
        if not self.access_token:
            return {'success': False, 'error': 'No authentication token'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Create deployment
            deployment_payload = {
                'versionNumber': 1,
                'manifestFileName': 'appsscript',
                'description': description
            }
            
            response = requests.post(
                f"{self.script_api_base}/projects/{script_id}/deployments",
                headers=headers,
                json=deployment_payload
            )
            
            if response.status_code == 200:
                deployment_data = response.json()
                return {
                    'success': True,
                    'deployment_id': deployment_data['deploymentId'],
                    'web_app_url': deployment_data.get('entryPoints', [{}])[0].get('webApp', {}).get('url'),
                    'deployment_data': deployment_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Deployment failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Deployment failed: {e}'
            }
    
    def execute_function(self, script_id: str, function_name: str, parameters: List = None) -> Dict:
        """Execute a function in a Google Apps Script project"""
        if not self.access_token:
            return {'success': False, 'error': 'No authentication token'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            execution_payload = {
                'function': function_name,
                'parameters': parameters or [],
                'devMode': True
            }
            
            response = requests.post(
                f"{self.script_api_base}/projects/{script_id}:run",
                headers=headers,
                json=execution_payload
            )
            
            if response.status_code == 200:
                result_data = response.json()
                return {
                    'success': True,
                    'result': result_data.get('response', {}).get('result'),
                    'execution_data': result_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Execution failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Function execution failed: {e}'
            }
    
    def _generate_gmail_template(self) -> str:
        """Generate Gmail automation template."""
        return '''function sendEmail() {
  const recipient = 'user@example.com';
  const subject = 'Automated Email';
  const body = 'This email was sent automatically from Google Apps Script.';
  
  GmailApp.sendEmail(recipient, subject, body);
}

function processInbox() {
  const threads = GmailApp.getInboxThreads(0, 10);
  threads.forEach(thread => {
    const messages = thread.getMessages();
    // Process messages
  });
}'''
    
    def _generate_sheet_template(self) -> str:
        """Generate Sheets processing template."""
        return '''function processSheetData() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // Process data
  data.forEach((row, index) => {
    if (index > 0) { // Skip header
      // Process each row
    }
  });
}

function addDataToSheet(values) {
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.appendRow(values);
}'''
    
    def _generate_calendar_template(self) -> str:
        """Generate Calendar sync template."""
        return '''function createCalendarEvent() {
  const calendar = CalendarApp.getDefaultCalendar();
  const event = calendar.createEvent(
    'Meeting Title',
    new Date('2024-01-01 10:00:00'),
    new Date('2024-01-01 11:00:00')
  );
  return event.getId();
}

function syncCalendarEvents() {
  const calendar = CalendarApp.getDefaultCalendar();
  const events = calendar.getEvents(
    new Date(),
    new Date(Date.now() + 24*60*60*1000)
  );
  // Sync events
}'''
    
    def _generate_drive_template(self) -> str:
        """Generate Drive organizer template."""
        return '''function organizeDriveFiles() {
  const folder = DriveApp.getFolderById('your-folder-id');
  const files = folder.getFiles();
  
  while (files.hasNext()) {
    const file = files.next();
    // Organize files by type, date, etc.
  }
}

function createFolder(name) {
  const folder = DriveApp.createFolder(name);
  return folder.getId();
}'''


class GoogleWorkspaceService:
    """Google Workspace integration service"""
    
    def __init__(self, gas_service: GoogleAppsScriptService):
        self.gas_service = gas_service
    
    def create_spreadsheet_integration(self, spreadsheet_config: Dict) -> str:
        """Create Google Apps Script code for spreadsheet integration"""
        
        template = f"""
function onEdit(e) {{
  // FlashFlow Spreadsheet Integration
  var range = e.range;
  var sheet = e.source.getActiveSheet();
  
  // Log changes to FlashFlow backend
  logChangeToFlashFlow({{
    sheet: sheet.getName(),
    range: range.getA1Notation(),
    oldValue: e.oldValue,
    newValue: e.value,
    user: Session.getActiveUser().getEmail(),
    timestamp: new Date().toISOString()
  }});
}}

function logChangeToFlashFlow(changeData) {{
  var webhookUrl = '{spreadsheet_config.get("webhook_url", "")}';
  if (!webhookUrl) return;
  
  var payload = {{
    'event_type': 'spreadsheet_change',
    'data': changeData,
    'spreadsheet_id': SpreadsheetApp.getActiveSpreadsheet().getId()
  }};
  
  var options = {{
    'method': 'POST',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  }};
  
  try {{
    UrlFetchApp.fetch(webhookUrl, options);
  }} catch (error) {{
    console.error('Failed to send webhook:', error);
  }}
}}

function syncDataToFlashFlow() {{
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  
  var apiUrl = '{spreadsheet_config.get("api_url", "")}';
  if (!apiUrl) return;
  
  var payload = {{
    'action': 'sync_spreadsheet_data',
    'spreadsheet_id': SpreadsheetApp.getActiveSpreadsheet().getId(),
    'sheet_name': sheet.getName(),
    'data': data
  }};
  
  var options = {{
    'method': 'POST',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'headers': {{
      'Authorization': 'Bearer {spreadsheet_config.get("auth_token", "")}'
    }}
  }};
  
  try {{
    var response = UrlFetchApp.fetch(apiUrl, options);
    console.log('Sync response:', response.getContentText());
  }} catch (error) {{
    console.error('Sync failed:', error);
  }}
}}

function importFromFlashFlow() {{
  var apiUrl = '{spreadsheet_config.get("import_url", "")}';
  if (!apiUrl) return;
  
  var options = {{
    'method': 'GET',
    'headers': {{
      'Authorization': 'Bearer {spreadsheet_config.get("auth_token", "")}'
    }}
  }};
  
  try {{
    var response = UrlFetchApp.fetch(apiUrl, options);
    var data = JSON.parse(response.getContentText());
    
    var sheet = SpreadsheetApp.getActiveSheet();
    sheet.clear();
    
    if (data.headers) {{
      sheet.getRange(1, 1, 1, data.headers.length).setValues([data.headers]);
    }}
    
    if (data.rows && data.rows.length > 0) {{
      sheet.getRange(2, 1, data.rows.length, data.rows[0].length).setValues(data.rows);
    }}
    
  }} catch (error) {{
    console.error('Import failed:', error);
  }}
}}
"""
        return template
    
    def create_form_integration(self, form_config: Dict) -> str:
        """Create Google Apps Script code for Google Forms integration"""
        
        template = f"""
function onFormSubmit(e) {{
  // FlashFlow Form Integration
  var form = FormApp.getActiveForm();
  var responses = e.response.getItemResponses();
  
  var formData = {{}};
  for (var i = 0; i < responses.length; i++) {{
    var response = responses[i];
    formData[response.getItem().getTitle()] = response.getResponse();
  }}
  
  // Send to FlashFlow backend
  sendFormDataToFlashFlow({{
    form_id: form.getId(),
    form_title: form.getTitle(),
    responses: formData,
    respondent_email: e.response.getRespondentEmail(),
    timestamp: new Date().toISOString()
  }});
}}

function sendFormDataToFlashFlow(submissionData) {{
  var webhookUrl = '{form_config.get("webhook_url", "")}';
  if (!webhookUrl) return;
  
  var payload = {{
    'event_type': 'form_submission',
    'data': submissionData
  }};
  
  var options = {{
    'method': 'POST',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  }};
  
  try {{
    var response = UrlFetchApp.fetch(webhookUrl, options);
    console.log('Form submission sent:', response.getContentText());
  }} catch (error) {{
    console.error('Failed to send form data:', error);
  }}
}}

function createFormFromFlashFlow() {{
  var apiUrl = '{form_config.get("form_definition_url", "")}';
  if (!apiUrl) return;
  
  var options = {{
    'method': 'GET',
    'headers': {{
      'Authorization': 'Bearer {form_config.get("auth_token", "")}'
    }}
  }};
  
  try {{
    var response = UrlFetchApp.fetch(apiUrl, options);
    var formDefinition = JSON.parse(response.getContentText());
    
    var form = FormApp.create(formDefinition.title || 'FlashFlow Generated Form');
    form.setDescription(formDefinition.description || 'Auto-generated from FlashFlow');
    
    // Add questions from definition
    if (formDefinition.questions) {{
      formDefinition.questions.forEach(function(question) {{
        switch (question.type) {{
          case 'text':
            form.addTextItem()
                .setTitle(question.title)
                .setRequired(question.required || false);
            break;
          case 'paragraph':
            form.addParagraphTextItem()
                .setTitle(question.title)
                .setRequired(question.required || false);
            break;
          case 'multiple_choice':
            var mcItem = form.addMultipleChoiceItem()
                .setTitle(question.title)
                .setRequired(question.required || false);
            if (question.choices) {{
              mcItem.setChoiceValues(question.choices);
            }}
            break;
          case 'email':
            form.addTextItem()
                .setTitle(question.title)
                .setRequired(question.required || false)
                .setValidation(FormApp.createTextValidation()
                    .setHelpText('Please enter a valid email address')
                    .requireTextIsEmail()
                    .build());
            break;
        }}
      }});
    }}
    
    console.log('Form created:', form.getEditUrl());
    return form.getId();
    
  }} catch (error) {{
    console.error('Form creation failed:', error);
  }}
}}
"""
        return template
    
    def create_document_integration(self, doc_config: Dict) -> str:
        """Create Google Apps Script code for Google Docs integration"""
        
        template = f"""
function generateDocumentFromFlashFlow() {{
  var apiUrl = '{doc_config.get("template_url", "")}';
  if (!apiUrl) return;
  
  var options = {{
    'method': 'GET',
    'headers': {{
      'Authorization': 'Bearer {doc_config.get("auth_token", "")}'
    }}
  }};
  
  try {{
    var response = UrlFetchApp.fetch(apiUrl, options);
    var templateData = JSON.parse(response.getContentText());
    
    // Create new document
    var doc = DocumentApp.create(templateData.title || 'FlashFlow Generated Document');
    var body = doc.getBody();
    
    // Add content from template
    if (templateData.content) {{
      templateData.content.forEach(function(section) {{
        switch (section.type) {{
          case 'heading':
            body.appendParagraph(section.text).setHeading(DocumentApp.ParagraphHeading.HEADING1);
            break;
          case 'paragraph':
            body.appendParagraph(section.text);
            break;
          case 'list':
            if (section.items) {{
              section.items.forEach(function(item) {{
                body.appendListItem(item);
              }});
            }}
            break;
          case 'table':
            if (section.data && section.data.length > 0) {{
              var table = body.appendTable(section.data);
              table.setBorderWidth(1);
            }}
            break;
        }}
      }});
    }}
    
    // Share document if specified
    if (templateData.share_with) {{
      templateData.share_with.forEach(function(email) {{
        doc.addEditor(email);
      }});
    }}
    
    console.log('Document created:', doc.getUrl());
    return doc.getId();
    
  }} catch (error) {{
    console.error('Document generation failed:', error);
  }}
}}

function syncDocumentToFlashFlow() {{
  var doc = DocumentApp.getActiveDocument();
  var content = doc.getBody().getText();
  
  var apiUrl = '{doc_config.get("sync_url", "")}';
  if (!apiUrl) return;
  
  var payload = {{
    'document_id': doc.getId(),
    'title': doc.getName(),
    'content': content,
    'last_modified': new Date().toISOString()
  }};
  
  var options = {{
    'method': 'POST',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'headers': {{
      'Authorization': 'Bearer {doc_config.get("auth_token", "")}'
    }}
  }};
  
  try {{
    var response = UrlFetchApp.fetch(apiUrl, options);
    console.log('Document synced:', response.getContentText());
  }} catch (error) {{
    console.error('Document sync failed:', error);
  }}
}}
"""
        return template


class FlashFlowGASIntegration:
    """Unified Google Apps Script integration for FlashFlow"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.gas_service = GoogleAppsScriptService(self.config)
        self.workspace_service = GoogleWorkspaceService(self.gas_service)
        self.active_projects = {}
    
    def setup_authentication(self, auth_config: Dict) -> bool:
        """Setup Google authentication"""
        return self.gas_service.setup_credentials(auth_config)
    
    def create_spreadsheet_automation(self, project_name: str, spreadsheet_config: Dict) -> Dict:
        """Create Google Apps Script for spreadsheet automation"""
        script_code = self.workspace_service.create_spreadsheet_integration(spreadsheet_config)
        
        result = self.gas_service.create_script_project(project_name, script_code)
        
        if result['success']:
            self.active_projects[project_name] = {
                'type': 'spreadsheet',
                'script_id': result['script_id'],
                'config': spreadsheet_config
            }
        
        return result
    
    def create_form_automation(self, project_name: str, form_config: Dict) -> Dict:
        """Create Google Apps Script for form automation"""
        script_code = self.workspace_service.create_form_integration(form_config)
        
        result = self.gas_service.create_script_project(project_name, script_code)
        
        if result['success']:
            self.active_projects[project_name] = {
                'type': 'form',
                'script_id': result['script_id'],
                'config': form_config
            }
        
        return result
    
    def create_document_automation(self, project_name: str, doc_config: Dict) -> Dict:
        """Create Google Apps Script for document automation"""
        script_code = self.workspace_service.create_document_integration(doc_config)
        
        result = self.gas_service.create_script_project(project_name, script_code)
        
        if result['success']:
            self.active_projects[project_name] = {
                'type': 'document',
                'script_id': result['script_id'],
                'config': doc_config
            }
        
        return result
    
    def deploy_all_projects(self) -> Dict:
        """Deploy all created Google Apps Script projects"""
        deployment_results = {}
        
        for project_name, project_info in self.active_projects.items():
            script_id = project_info['script_id']
            
            result = self.gas_service.deploy_web_app(
                script_id, 
                f"FlashFlow {project_info['type']} automation"
            )
            
            deployment_results[project_name] = result
        
        return {
            'success': True,
            'deployments': deployment_results,
            'total_projects': len(self.active_projects)
        }
    
    def get_project_info(self) -> Dict:
        """Get information about active Google Apps Script projects"""
        return {
            'total_projects': len(self.active_projects),
            'projects': self.active_projects,
            'authentication_status': self.gas_service.access_token is not None
        }