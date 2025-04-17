import { Component, OnInit } from '@angular/core';
import { NgClass, NgForOf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';
import { DatePipe } from '@angular/common';

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
  imports: [NgClass, NgForOf, FormsModule, DropdownModule, DatePipe],
})
export class NotificationsComponent implements OnInit {
  notificationTypes = [
    { label: 'All',         value: 'all'         },
    { label: 'Critical',    value: 'critical'    },
    { label: 'Monitor',     value: 'monitor'     },
    { label: 'Information', value: 'information' },
  ];

  selectedType: string = 'all';
  originalNotifications: NotificationItem[] = [];

  constructor(private notificationsService: NotificationsService) {}

  ngOnInit(): void {
    this.loadNotifications();
  }

  private loadNotifications(): void {
    // getNotifications returns an Observable<PatientAlertsBackend>
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
        timestamp: new Date() //TODO: when we add dates to the db
      }))
      .filter(n => n.type !== null) as NotificationItem[];
  }

  filteredNotifications(): NotificationItem[] {
    if (this.selectedType === 'all') {
      return this.originalNotifications;
    }
    return this.originalNotifications.filter(n => n.type === this.selectedType);
  }
}