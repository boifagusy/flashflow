"""
Cloud Services Integration Layer for FlashFlow
==============================================

Integration layer that connects cloud services with FlashFlow's component system.
"""

import os
import json
from typing import Dict, List, Any, Optional
from ..services.cloud_services import CloudServicesManager

class CloudIntegrationLayer:
    """Integration layer for cloud services in FlashFlow"""
    
    def __init__(self):
        self.cloud_manager = CloudServicesManager()
    
    def generate_cloud_components(self, project_path: str, cloud_config: Dict) -> Dict[str, str]:
        """Generate React components for cloud services"""
        components = {}
        
        if cloud_config.get('firebase', {}).get('enabled'):
            components['FirebaseAuth'] = self._generate_firebase_auth_component()
            components['FirestoreManager'] = self._generate_firestore_component()
            components['FirebaseStorage'] = self._generate_firebase_storage_component()
        
        if cloud_config.get('supabase', {}).get('enabled'):
            components['SupabaseAuth'] = self._generate_supabase_auth_component()
            components['SupabaseData'] = self._generate_supabase_data_component()
        
        if cloud_config.get('aws', {}).get('enabled'):
            components['AWSUploader'] = self._generate_aws_uploader_component()
        
        return components
    
    def _generate_firebase_auth_component(self) -> str:
        """Generate Firebase authentication component"""
        return '''import React, { useState, useEffect } from 'react';
import { auth } from '../config/firebase';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from 'firebase/auth';

export const FirebaseAuth = () => {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(setUser);
    return unsubscribe;
  }, []);

  const signIn = async () => {
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
      console.error('Sign in error:', error);
    }
    setLoading(false);
  };

  const signUp = async () => {
    setLoading(true);
    try {
      await createUserWithEmailAndPassword(auth, email, password);
    } catch (error) {
      console.error('Sign up error:', error);
    }
    setLoading(false);
  };

  const handleSignOut = () => signOut(auth);

  if (user) {
    return (
      <div className="auth-container">
        <p>Welcome, {user.email}</p>
        <button onClick={handleSignOut}>Sign Out</button>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={signIn} disabled={loading}>Sign In</button>
      <button onClick={signUp} disabled={loading}>Sign Up</button>
    </div>
  );
};'''

    def _generate_firestore_component(self) -> str:
        """Generate Firestore data management component"""
        return '''import React, { useState, useEffect } from 'react';
import { db } from '../config/firebase';
import { collection, addDoc, getDocs, doc, updateDoc, deleteDoc } from 'firebase/firestore';

export const FirestoreManager = ({ collectionName = 'items' }) => {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadItems();
  }, [collectionName]);

  const loadItems = async () => {
    setLoading(true);
    try {
      const querySnapshot = await getDocs(collection(db, collectionName));
      const itemsData = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setItems(itemsData);
    } catch (error) {
      console.error('Error loading items:', error);
    }
    setLoading(false);
  };

  const addItem = async () => {
    if (!newItem.trim()) return;
    
    try {
      await addDoc(collection(db, collectionName), {
        name: newItem,
        createdAt: new Date()
      });
      setNewItem('');
      loadItems();
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  const deleteItem = async (id) => {
    try {
      await deleteDoc(doc(db, collectionName, id));
      loadItems();
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  return (
    <div className="firestore-manager">
      <h3>Firestore Manager - {collectionName}</h3>
      
      <div className="add-item">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          placeholder="Enter new item"
        />
        <button onClick={addItem}>Add Item</button>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="items-list">
          {items.map(item => (
            <div key={item.id} className="item">
              <span>{item.name}</span>
              <button onClick={() => deleteItem(item.id)}>Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};'''

    def _generate_firebase_storage_component(self) -> str:
        """Generate Firebase Storage component"""
        return '''import React, { useState } from 'react';
import { storage } from '../config/firebase';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';

export const FirebaseStorage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [downloadURL, setDownloadURL] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const storageRef = ref(storage, `files/${file.name}`);
      const snapshot = await uploadBytes(storageRef, file);
      const url = await getDownloadURL(snapshot.ref);
      setDownloadURL(url);
      console.log('File uploaded successfully');
    } catch (error) {
      console.error('Upload error:', error);
    }
    setUploading(false);
  };

  return (
    <div className="firebase-storage">
      <h3>Firebase Storage</h3>
      
      <input type="file" onChange={handleFileChange} />
      <button onClick={uploadFile} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload File'}
      </button>

      {downloadURL && (
        <div className="download-link">
          <p>File uploaded successfully!</p>
          <a href={downloadURL} target="_blank" rel="noopener noreferrer">
            View File
          </a>
        </div>
      )}
    </div>
  );
};'''

    def _generate_supabase_auth_component(self) -> str:
        """Generate Supabase authentication component"""
        return '''import React, { useState, useEffect } from 'react';
import { supabase } from '../config/supabase';

export const SupabaseAuth = () => {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user || null);
    });
    return () => subscription.unsubscribe();
  }, []);

  const signIn = async () => {
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) console.error('Sign in error:', error);
    setLoading(false);
  };

  const signUp = async () => {
    setLoading(true);
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) console.error('Sign up error:', error);
    setLoading(false);
  };

  const handleSignOut = () => supabase.auth.signOut();

  if (user) {
    return (
      <div className="auth-container">
        <p>Welcome, {user.email}</p>
        <button onClick={handleSignOut}>Sign Out</button>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={signIn} disabled={loading}>Sign In</button>
      <button onClick={signUp} disabled={loading}>Sign Up</button>
    </div>
  );
};'''

    def _generate_supabase_data_component(self) -> str:
        """Generate Supabase data management component"""
        return '''import React, { useState, useEffect } from 'react';
import { supabase } from '../config/supabase';

export const SupabaseData = ({ tableName = 'items' }) => {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadItems();
  }, [tableName]);

  const loadItems = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from(tableName)
        .select('*')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      setItems(data || []);
    } catch (error) {
      console.error('Error loading items:', error);
    }
    setLoading(false);
  };

  const addItem = async () => {
    if (!newItem.trim()) return;
    
    try {
      const { error } = await supabase
        .from(tableName)
        .insert([{ name: newItem }]);
      
      if (error) throw error;
      setNewItem('');
      loadItems();
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  const deleteItem = async (id) => {
    try {
      const { error } = await supabase
        .from(tableName)
        .delete()
        .eq('id', id);
      
      if (error) throw error;
      loadItems();
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  return (
    <div className="supabase-data">
      <h3>Supabase Data - {tableName}</h3>
      
      <div className="add-item">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          placeholder="Enter new item"
        />
        <button onClick={addItem}>Add Item</button>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="items-list">
          {items.map(item => (
            <div key={item.id} className="item">
              <span>{item.name}</span>
              <button onClick={() => deleteItem(item.id)}>Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};'''

    def _generate_aws_uploader_component(self) -> str:
        """Generate AWS S3 uploader component"""
        return '''import React, { useState } from 'react';

export const AWSUploader = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/cloud/aws/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (result.success) {
        setUploadResult(result);
        console.log('File uploaded successfully');
      } else {
        console.error('Upload failed:', result.error);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
    setUploading(false);
  };

  return (
    <div className="aws-uploader">
      <h3>AWS S3 Uploader</h3>
      
      <input type="file" onChange={handleFileChange} />
      <button onClick={uploadFile} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload to S3'}
      </button>

      {uploadResult && (
        <div className="upload-result">
          <p>File uploaded successfully!</p>
          <a href={uploadResult.url} target="_blank" rel="noopener noreferrer">
            View File
          </a>
        </div>
      )}
    </div>
  );
};'''
    
    def generate_flask_routes(self, cloud_config: Dict) -> str:
        """Generate Flask routes for cloud services"""
        return '''from flask import Blueprint, request, jsonify
from ..services.cloud_services import CloudServicesManager

cloud_bp = Blueprint('cloud', __name__, url_prefix='/api/cloud')
cloud_manager = CloudServicesManager()

@cloud_bp.route('/initialize/<provider>', methods=['POST'])
def initialize_provider(provider):
    """Initialize cloud provider"""
    try:
        config = request.json
        result = cloud_manager.initialize_provider(provider, config)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cloud_bp.route('/status', methods=['GET'])
def get_status():
    """Get cloud provider status"""
    try:
        status = cloud_manager.get_provider_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cloud_bp.route('/firebase/auth/create', methods=['POST'])
def firebase_create_user():
    """Create Firebase user"""
    try:
        data = request.json
        result = cloud_manager.firebase.create_user(
            data['email'], 
            data['password']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cloud_bp.route('/firebase/firestore/create', methods=['POST'])
def firebase_create_document():
    """Create Firestore document"""
    try:
        data = request.json
        result = cloud_manager.firebase.create_firestore_document(
            data['collection'],
            data['document_id'],
            data['data']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cloud_bp.route('/supabase/auth/signup', methods=['POST'])
def supabase_signup():
    """Supabase user signup"""
    try:
        data = request.json
        result = cloud_manager.supabase.sign_up_user(
            data['email'], 
            data['password']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cloud_bp.route('/supabase/data/insert', methods=['POST'])
def supabase_insert():
    """Insert data into Supabase table"""
    try:
        data = request.json
        result = cloud_manager.supabase.insert_record(
            data['table'],
            data['record']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cloud_bp.route('/aws/s3/upload', methods=['POST'])
def aws_s3_upload():
    """Upload file to AWS S3"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        # Save file temporarily and upload to S3
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        result = cloud_manager.aws.upload_to_s3(
            'your-bucket-name',
            file.filename,
            temp_path
        )
        
        # Clean up temp file
        import os
        os.remove(temp_path)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})'''

    def create_demo_flow(self, project_path: str) -> str:
        """Create demo .flow file for cloud services"""
        return '''# Cloud Services Integration Demo
app "Cloud Demo" {
    title: "Cloud Services Demo"
    description: "Demonstrating FlashFlow cloud integrations"
    
    # Cloud configuration
    cloud_config {
        firebase: {
            enabled: true
            project_id: "flashflow-demo"
            api_key: "your-firebase-api-key"
            auth_domain: "flashflow-demo.firebaseapp.com"
            services: ["auth", "firestore", "storage", "functions"]
        }
        
        supabase: {
            enabled: true
            project_url: "https://your-project.supabase.co"
            anon_key: "your-supabase-anon-key"
            services: ["auth", "database", "storage", "edge_functions"]
        }
        
        aws: {
            enabled: false
            access_key_id: "your-aws-access-key"
            secret_access_key: "your-aws-secret-key"
            region: "us-east-1"
            services: ["s3", "lambda", "dynamodb"]
        }
    }
}

# Firebase Authentication Page
page firebase_auth {
    title: "Firebase Auth"
    
    component FirebaseAuth {
        providers: ["email", "google", "github"]
        redirect_url: "/dashboard"
        
        events: {
            onSignIn: handle_firebase_signin
            onSignUp: handle_firebase_signup
            onSignOut: handle_firebase_signout
        }
    }
    
    component FirestoreManager {
        collection: "users"
        real_time: true
        
        schema: {
            name: "string"
            email: "string"
            created_at: "timestamp"
        }
    }
}

# Supabase Integration Page
page supabase_demo {
    title: "Supabase Demo"
    
    component SupabaseAuth {
        enable_magic_link: true
        social_providers: ["google", "github"]
        
        events: {
            onAuthChange: handle_supabase_auth
        }
    }
    
    component SupabaseData {
        table: "posts"
        enable_realtime: true
        
        policies: {
            select: "authenticated"
            insert: "authenticated"
            update: "user_id == auth.uid()"
            delete: "user_id == auth.uid()"
        }
    }
}

# Cloud Storage Page
page cloud_storage {
    title: "Cloud Storage"
    
    component FirebaseStorage {
        bucket: "flashflow-demo.appspot.com"
        max_file_size: "10MB"
        allowed_types: ["image", "document", "video"]
        
        events: {
            onUploadStart: show_progress
            onUploadComplete: handle_upload_complete
            onUploadError: handle_upload_error
        }
    }
    
    component AWSUploader {
        bucket: "flashflow-uploads"
        region: "us-east-1"
        
        settings: {
            public_read: false
            server_side_encryption: true
        }
    }
}

# API Routes
api cloud_api {
    base_path: "/api/cloud"
    
    endpoints: {
        "POST /initialize/:provider": initialize_cloud_provider
        "GET /status": get_cloud_status
        "POST /firebase/auth/create": create_firebase_user
        "POST /firebase/firestore/create": create_firestore_document
        "POST /supabase/auth/signup": supabase_user_signup
        "POST /supabase/data/insert": insert_supabase_record
        "POST /aws/s3/upload": upload_to_s3
    }
}

# Event Handlers
handlers {
    handle_firebase_signin(user) {
        log("Firebase user signed in: " + user.email)
        redirect("/dashboard")
        
        # Create user profile in Firestore
        create_firestore_document("user_profiles", user.uid, {
            email: user.email,
            last_login: now(),
            provider: "firebase"
        })
    }
    
    handle_supabase_auth(event, session) {
        if (event == "SIGNED_IN") {
            log("Supabase user signed in: " + session.user.email)
            
            # Update user metadata
            update_supabase_record("profiles", session.user.id, {
                last_seen: now(),
                online_status: true
            })
        }
    }
    
    handle_upload_complete(file_data) {
        log("File uploaded: " + file_data.name)
        
        # Save file metadata to database
        if (current_provider == "firebase") {
            create_firestore_document("uploads", generate_id(), file_data)
        } else if (current_provider == "supabase") {
            insert_supabase_record("uploads", file_data)
        }
    }
}

# Background Jobs
jobs {
    # Sync data between providers
    sync_cloud_data {
        schedule: "0 */6 * * *"  # Every 6 hours
        
        task() {
            # Backup Firebase data to Supabase
            firebase_collections = ["users", "posts", "uploads"]
            
            for collection in firebase_collections {
                firebase_data = get_firestore_collection(collection)
                backup_to_supabase(collection + "_backup", firebase_data)
            }
            
            log("Cloud data sync completed")
        }
    }
    
    # Clean up old files
    cleanup_storage {
        schedule: "0 3 * * 0"  # Weekly at 3 AM Sunday
        
        task() {
            # Remove files older than 90 days
            cutoff_date = date_subtract(now(), days: 90)
            
            old_files = query_files(uploaded_before: cutoff_date)
            for file in old_files {
                delete_cloud_file(file.provider, file.path)
                delete_file_record(file.id)
            }
            
            log("Storage cleanup completed: " + old_files.length + " files removed")
        }
    }
}'''