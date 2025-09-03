#!/usr/bin/env python3
"""
Script de surveillance pour GitHub Actions
Vérifie si tickets.cafonline.com est sorti de maintenance
"""

import requests
import json
import os
import sys
from datetime import datetime

def check_site_status():
    """
    Vérifie l'état du site tickets.cafonline.com
    
    Returns:
        bool: True si le site est accessible, False sinon
    """
    site_url = "https://tickets.cafonline.com/"
    
    try:
        response = requests.get(site_url, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Statut HTTP: {response.status_code}")
            return False
        
        content = response.text.lower()
        
        maintenance_keywords = [
            'site en maintenance',
            'en cours de maintenance',
            'maintenance',
            'temporarily unavailable',
            'under construction'
        ]
        
        has_maintenance = any(keyword in content for keyword in maintenance_keywords)
        
        if has_maintenance:
            print(f"🔧 Site toujours en maintenance")
            return False
        else:
            print(f"✅ Site accessible ! Plus de page de maintenance détectée")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def send_ifttt_notification():
    """
    Envoie une notification via IFTTT webhook
    """
    webhook_url = os.environ.get('IFTTT_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ Variable d'environnement IFTTT_WEBHOOK_URL non définie")
        return False
    
    try:
        data = {
            "value1": "tickets.cafonline.com",
            "value2": "🎉 Le site de billetterie CAN 2025 est de nouveau accessible !",
            "value3": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        response = requests.post(webhook_url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Notification IFTTT envoyée avec succès !")
            return True
        else:
            print(f"❌ Erreur IFTTT: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi de la notification: {e}")
        return False

def main():
    """
    Fonction principale pour GitHub Actions
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] 🔍 Vérification GitHub Actions de tickets.cafonline.com...")
    
    is_accessible = check_site_status()
    
    if is_accessible:
        print(f"🎉 SITE ACCESSIBLE ! Envoi de la notification...")
        success = send_ifttt_notification()
        if success:
            print(f"✅ Mission accomplie ! Notification envoyée.")
            # Créer un fichier pour indiquer le succès
            with open('site_accessible.flag', 'w') as f:
                f.write(f"Site accessible détecté le {current_time}")
            sys.exit(0)
        else:
            print(f"❌ Échec de l'envoi de la notification")
            sys.exit(1)
    else:
        print(f"⏳ Site toujours en maintenance")
        sys.exit(0)  # Pas d'erreur, juste en attente

if __name__ == "__main__":
    main()

