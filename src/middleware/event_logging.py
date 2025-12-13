"""
Event Logging Middleware
Provides decorators and utilities for logging dashboard events
"""

import functools
import logging
from datetime import datetime, timezone
from flask import request, g
from typing import Dict, Optional, Any

from src.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)


class EventLogger:
    """Event logging utility class"""
    
    def __init__(self):
        self._mongodb_service = None
    
    @property
    def mongodb_service(self):
        """Lazy initialization of MongoDB service"""
        if self._mongodb_service is None:
            self._mongodb_service = MongoDBService()
        return self._mongodb_service
    
    def log_user_event(self, action: str, user_data: Dict) -> bool:
        """Log a user-related event"""
        try:
            event = {
                'event_type': f'user.{action}',
                'user_id': user_data.get('user_id'),
                'timestamp': datetime.now(timezone.utc),
                'source': 'api',
                'details': {
                    'username': user_data.get('username'),
                    'email': user_data.get('email'),
                    **{k: v for k, v in user_data.items() if k not in ['user_id']}
                }
            }
            
            result = self.mongodb_service.log_event(event)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to log user event {action}: {e}")
            return False
    
    def log_device_event(self, action: str, device_data: Dict) -> bool:
        """Log a device-related event"""
        try:
            event = {
                'event_type': f'device.{action}',
                'device_id': device_data.get('device_id'),
                'user_id': device_data.get('user_id'),
                'timestamp': datetime.now(timezone.utc),
                'source': 'api',
                'details': {
                    'device_name': device_data.get('name'),
                    'device_type': device_data.get('device_type'),
                    'location': device_data.get('location'),
                    **{k: v for k, v in device_data.items() if k not in ['device_id', 'user_id']}
                }
            }
            
            result = self.mongodb_service.log_event(event)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to log device event {action}: {e}")
            return False
    
    def log_telemetry_event(self, action: str, telemetry_data: Dict) -> bool:
        """Log a telemetry-related event"""
        try:
            data = telemetry_data.get('data', {})
            event = {
                'event_type': f'telemetry.{action}',
                'device_id': telemetry_data.get('device_id'),
                'user_id': telemetry_data.get('user_id'),
                'timestamp': telemetry_data.get('timestamp', datetime.now(timezone.utc)),
                'source': 'api',
                'details': {
                    'data_points': len(data) if isinstance(data, dict) else 0,
                    'measurements': list(data.keys()) if isinstance(data, dict) else [],
                    'data_size_bytes': len(str(data)),
                    **{k: v for k, v in telemetry_data.items() if k not in ['device_id', 'user_id', 'data']}
                }
            }
            
            result = self.mongodb_service.log_event(event)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to log telemetry event {action}: {e}")
            return False
    
    def log_event(self, event_type: str, user_id: Optional[int] = None, 
                  device_id: Optional[int] = None, details: Optional[Dict] = None) -> bool:
        """Log an event to MongoDB"""
        try:
            if not self.mongodb_service.is_available():
                logger.warning("MongoDB not available, skipping event logging")
                return False
            
            event = {
                'event_type': event_type,
                'timestamp': datetime.now(timezone.utc),
                'source': 'api',
                'details': details or {}
            }
            
            # Add request context if available
            if request:
                event['details'].update({
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'url': request.url
                })
            
            if user_id:
                event['user_id'] = user_id
            
            if device_id:
                event['device_id'] = device_id
            
            result = self.mongodb_service.log_event(event)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to log event {event_type}: {e}")
            return False


# Global event logger instance
event_logger = EventLogger()


def log_user_action(action: str, details: Optional[Dict] = None):
    """Decorator to log user actions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            # Log the event after successful execution
            try:
                user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
                if user_id:
                    user_id = int(user_id)
                
                event_details = details.copy() if details else {}
                
                # Add response status if available
                if hasattr(result, 'status_code'):
                    event_details['response_status'] = result.status_code
                
                event_logger.log_event(f'user.{action}', user_id=user_id, details=event_details)
                
            except Exception as e:
                logger.error(f"Failed to log user action {action}: {e}")
            
            return result
        return wrapper
    return decorator


def log_device_action(action: str, details: Optional[Dict] = None):
    """Decorator to log device actions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            # Log the event after successful execution
            try:
                user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
                device_id = kwargs.get('device_id') or request.view_args.get('device_id')
                
                if user_id:
                    user_id = int(user_id)
                if device_id:
                    device_id = int(device_id)
                
                event_details = details.copy() if details else {}
                
                # Add response status if available
                if hasattr(result, 'status_code'):
                    event_details['response_status'] = result.status_code
                
                event_logger.log_event(
                    f'device.{action}', 
                    user_id=user_id, 
                    device_id=device_id, 
                    details=event_details
                )
                
            except Exception as e:
                logger.error(f"Failed to log device action {action}: {e}")
            
            return result
        return wrapper
    return decorator


def log_system_action(action: str, details: Optional[Dict] = None):
    """Decorator to log system actions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            # Log the event after successful execution
            try:
                user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
                if user_id:
                    user_id = int(user_id)
                
                event_details = details.copy() if details else {}
                
                # Add response status if available
                if hasattr(result, 'status_code'):
                    event_details['response_status'] = result.status_code
                
                event_logger.log_event(f'system.{action}', user_id=user_id, details=event_details)
                
            except Exception as e:
                logger.error(f"Failed to log system action {action}: {e}")
            
            return result
        return wrapper
    return decorator


def log_api_call(event_type: str = None, include_request_data: bool = False):
    """Generic decorator to log API calls"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now(timezone.utc)
            
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Log the event after execution
            try:
                end_time = datetime.now(timezone.utc)
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
                device_id = request.headers.get('X-API-Key')  # Could map to device
                
                if user_id:
                    user_id = int(user_id)
                
                event_details = {
                    'duration_ms': duration_ms,
                    'function_name': func.__name__
                }
                
                if include_request_data and request.is_json:
                    event_details['request_data_size'] = len(request.get_data())
                
                # Add response status if available
                if hasattr(result, 'status_code'):
                    event_details['response_status'] = result.status_code
                
                # Determine event type
                if not event_type:
                    endpoint = request.endpoint or func.__name__
                    auto_event_type = f'api.{endpoint.replace(".", "_")}'
                else:
                    auto_event_type = event_type
                
                event_logger.log_event(
                    auto_event_type, 
                    user_id=user_id, 
                    details=event_details
                )
                
            except Exception as e:
                logger.error(f"Failed to log API call {func.__name__}: {e}")
            
            return result
        return wrapper
    return decorator


def log_authentication_event(event_type: str, user_id: Optional[int] = None, 
                           success: bool = True, details: Optional[Dict] = None):
    """Log authentication events"""
    try:
        event_details = details.copy() if details else {}
        event_details.update({
            'success': success,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent', '') if request else ''
        })
        
        event_logger.log_event(f'auth.{event_type}', user_id=user_id, details=event_details)
        
    except Exception as e:
        logger.error(f"Failed to log authentication event {event_type}: {e}")


def log_error_event(error_type: str, error_details: Dict, user_id: Optional[int] = None):
    """Log error events"""
    try:
        event_details = {
            'error_type': error_type,
            'error_details': error_details,
            'endpoint': request.endpoint if request else None,
            'method': request.method if request else None
        }
        
        event_logger.log_event(f'error.{error_type}', user_id=user_id, details=event_details)
        
    except Exception as e:
        logger.error(f"Failed to log error event {error_type}: {e}")


def log_performance_event(metric_name: str, value: float, threshold: Optional[float] = None,
                        user_id: Optional[int] = None, details: Optional[Dict] = None):
    """Log performance events"""
    try:
        event_details = details.copy() if details else {}
        event_details.update({
            'metric_name': metric_name,
            'value': value,
            'threshold': threshold,
            'exceeded_threshold': threshold and value > threshold
        })
        
        event_logger.log_event(f'performance.{metric_name}', user_id=user_id, details=event_details)
        
    except Exception as e:
        logger.error(f"Failed to log performance event {metric_name}: {e}")


# Convenience functions for common events
def log_login(user_id: int, success: bool = True, details: Optional[Dict] = None):
    """Log user login event"""
    log_authentication_event('login', user_id, success, details)


def log_logout(user_id: int, details: Optional[Dict] = None):
    """Log user logout event"""
    log_authentication_event('logout', user_id, True, details)


def log_device_registration(user_id: int, device_id: int, device_details: Dict):
    """Log device registration event"""
    event_logger.log_event('device.registered', user_id=user_id, device_id=device_id, 
                          details=device_details)


def log_telemetry_received(user_id: int, device_id: int, telemetry_details: Dict):
    """Log telemetry data received event"""
    event_logger.log_event('device.telemetry_received', user_id=user_id, device_id=device_id,
                          details=telemetry_details)


def log_alert_created(user_id: int, device_id: int, alert_details: Dict):
    """Log alert creation event"""
    event_logger.log_event('device.alert_created', user_id=user_id, device_id=device_id,
                          details=alert_details)