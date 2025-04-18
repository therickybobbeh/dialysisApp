import { Component, OnInit } from '@angular/core';
import { NgClass, NgForOf, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';
import { DatePipe } from '@angular/common';
import {ButtonDirective, ButtonIcon, ButtonLabel} from 'primeng/button';
import { Tooltip } from 'primeng/tooltip';

import {
  mapBackendDataToPatientAlerts,
  PatientAlertsBackend,
  AlertType
} from '../../Models/notifications';
import { NotificationsService } from '../../Services/notifications.service';

interface NotificationItem {
  message: string;
  type: AlertType;
  timestamp?: Date;
}

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss'],
  imports: [NgClass, NgForOf, NgIf, FormsModule, DropdownModule, DatePipe, ButtonDirective, Tooltip, ButtonIcon, ButtonLabel]
})
export class NotificationsComponent implements OnInit {
  notificationTypes = [
    { label: 'All',         value: 'all'         },
    { label: 'Critical',    value: 'critical'    },
    { label: 'Monitor',     value: 'monitor'     },
    { label: 'Information', value: 'information' }
  ];

  selectedType: string = 'all';
  originalNotifications: NotificationItem[] = [];

  constructor(private notificationsService: NotificationsService) {}

  ngOnInit(): void {
    this.notificationsService.getNotifications().then(obs => {
      obs.subscribe({
        next: (data: PatientAlertsBackend) => {
          this.originalNotifications = this.mapNotifications(data);
        },
        error: err => console.error('Error fetching notifications:', err)
      });
    });
  }

  private mapNotifications(data: PatientAlertsBackend): NotificationItem[] {
    const frontend = mapBackendDataToPatientAlerts(data);
    return (Object.keys(frontend) as Array<keyof typeof frontend>)
      .map(key => ({
        message: frontend[key].message,
        type: frontend[key].type,
        timestamp: new Date()
      }))
      .filter(n => n.type !== null) as NotificationItem[];
  }

  filteredNotifications(): NotificationItem[] {
    if (this.selectedType === 'all') {
      return this.originalNotifications;
    }
    return this.originalNotifications.filter(n => n.type === this.selectedType);
  }

  dismissOne(index: number) {
    this.originalNotifications.splice(index, 1);
  }

  dismissAll() {
    this.originalNotifications = [];
  }
}