"""
Session management utilities for OkuoAgent.
Provides manual cleanup and monitoring functions for the session manager.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.logger import logger


def get_session_manager():
    """Get the global session manager instance."""
    from core.graph.tools import session_manager
    return session_manager


def manual_cleanup_all_sessions():
    """Limpia manualmente todas las sesiones activas."""
    try:
        session_manager = get_session_manager()
        session_manager.cleanup_old_sessions()
        logger.info("Manual cleanup of all sessions completed")
        return True
    except Exception as e:
        logger.error(f"Error during manual cleanup: {e}")
        return False


def cleanup_specific_session(session_id: str):
    """Limpia una sesión específica."""
    try:
        session_manager = get_session_manager()
        session_manager.cleanup_session(session_id)
        logger.info(f"Manual cleanup of session {session_id} completed")
        return True
    except Exception as e:
        logger.error(f"Error cleaning session {session_id}: {e}")
        return False


def get_sessions_summary() -> Dict:
    """Obtiene un resumen de todas las sesiones activas."""
    try:
        session_manager = get_session_manager()
        sessions_info = session_manager.get_all_sessions_info()
        
        total_sessions = len(sessions_info)
        total_memory = sum(s.get('memory_usage_mb', 0) for s in sessions_info)
        total_variables = sum(s.get('variable_count', 0) for s in sessions_info)
        total_images = sum(s.get('image_count', 0) for s in sessions_info)
        
        # Encontrar sesiones más antiguas
        old_sessions = [s for s in sessions_info if s.get('age_hours', 0) > 12]
        inactive_sessions = [s for s in sessions_info if s.get('inactive_hours', 0) > 6]
        
        return {
            'total_sessions': total_sessions,
            'total_memory_mb': total_memory,
            'total_variables': total_variables,
            'total_images': total_images,
            'old_sessions_count': len(old_sessions),
            'inactive_sessions_count': len(inactive_sessions),
            'sessions_detail': sessions_info
        }
    except Exception as e:
        logger.error(f"Error getting sessions summary: {e}")
        return {}


def cleanup_old_image_files(max_age_hours: int = 24):
    """Limpia archivos de imagen antiguos que no están asociados a sesiones activas."""
    try:
        from config import config
        
        if not os.path.exists(config.IMAGES_DIR):
            return
        
        session_manager = get_session_manager()
        active_sessions = session_manager.get_all_sessions_info()
        active_image_files = set()
        
        # Recopilar todos los archivos de imagen activos
        for session_info in active_sessions:
            session_id = session_info.get('session_id')
            if session_id:
                session_data = session_manager.get_session(session_id)
                active_image_files.update(session_data.get('image_files', []))
        
        # Encontrar archivos antiguos
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        files_to_remove = []
        
        for filename in os.listdir(config.IMAGES_DIR):
            if not filename.endswith('.pkl'):
                continue
            
            filepath = os.path.join(config.IMAGES_DIR, filename)
            try:
                file_age = current_time - os.path.getctime(filepath)
                if file_age > max_age_seconds and filename not in active_image_files:
                    files_to_remove.append(filename)
            except:
                continue
        
        # Eliminar archivos antiguos
        removed_count = 0
        for filename in files_to_remove:
            try:
                filepath = os.path.join(config.IMAGES_DIR, filename)
                os.remove(filepath)
                removed_count += 1
                logger.info(f"Removed old image file: {filename}")
            except Exception as e:
                logger.warning(f"Failed to remove old image file {filename}: {e}")
        
        logger.info(f"Cleanup completed: {removed_count} old image files removed")
        return removed_count
        
    except Exception as e:
        logger.error(f"Error during image cleanup: {e}")
        return 0


def get_system_health_report() -> Dict:
    """Genera un reporte completo de salud del sistema."""
    try:
        sessions_summary = get_sessions_summary()
        
        # Calcular métricas de salud
        health_status = {
            'overall_status': 'healthy',
            'warnings': [],
            'critical_issues': []
        }
        
        # Verificar memoria total
        total_memory = sessions_summary.get('total_memory_mb', 0)
        if total_memory > 500:  # 500MB total
            health_status['warnings'].append(f"High total memory usage: {total_memory:.1f}MB")
            if total_memory > 1000:  # 1GB total
                health_status['critical_issues'].append("Critical total memory usage")
                health_status['overall_status'] = 'critical'
        
        # Verificar número de sesiones
        total_sessions = sessions_summary.get('total_sessions', 0)
        if total_sessions > 10:
            health_status['warnings'].append(f"High number of active sessions: {total_sessions}")
        
        # Verificar sesiones antiguas
        old_sessions = sessions_summary.get('old_sessions_count', 0)
        if old_sessions > 0:
            health_status['warnings'].append(f"Old sessions detected: {old_sessions}")
        
        # Verificar sesiones inactivas
        inactive_sessions = sessions_summary.get('inactive_sessions_count', 0)
        if inactive_sessions > 0:
            health_status['warnings'].append(f"Inactive sessions detected: {inactive_sessions}")
        
        # Verificar archivos de imagen
        total_images = sessions_summary.get('total_images', 0)
        if total_images > 100:
            health_status['warnings'].append(f"High number of image files: {total_images}")
        
        if health_status['critical_issues']:
            health_status['overall_status'] = 'critical'
        elif health_status['warnings']:
            health_status['overall_status'] = 'warning'
        
        return {
            'health_status': health_status,
            'sessions_summary': sessions_summary,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating health report: {e}")
        return {
            'health_status': {
                'overall_status': 'error',
                'warnings': [f"Error generating health report: {e}"],
                'critical_issues': []
            },
            'sessions_summary': {},
            'timestamp': datetime.now().isoformat()
        }


def force_garbage_collection():
    """Fuerza la recolección de basura del sistema."""
    try:
        import gc
        collected = gc.collect()
        logger.info(f"Garbage collection completed: {collected} objects collected")
        return collected
    except Exception as e:
        logger.error(f"Error during garbage collection: {e}")
        return 0


def get_memory_usage_breakdown() -> Dict:
    """Obtiene un desglose detallado del uso de memoria."""
    try:
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        sessions_summary = get_sessions_summary()
        session_memory = sessions_summary.get('total_memory_mb', 0)
        
        return {
            'process_rss_mb': memory_info.rss / (1024 * 1024),
            'process_vms_mb': memory_info.vms / (1024 * 1024),
            'session_memory_mb': session_memory,
            'system_memory_percent': psutil.virtual_memory().percent,
            'system_available_mb': psutil.virtual_memory().available / (1024 * 1024)
        }
    except Exception as e:
        logger.error(f"Error getting memory breakdown: {e}")
        return {} 