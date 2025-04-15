import { Component } from '@angular/core';
import {DropdownModule} from "primeng/dropdown";
import {DatePipe, NgClass, NgForOf} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {Select} from "primeng/select";

@Component({
  selector: 'app-notifications',
  imports: [
    DropdownModule,
    NgClass,
    FormsModule,
    NgForOf,
    DatePipe,
    Select
  ],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.scss'
})
export class NotificationsComponent {
  notificationTypes = [
    { label: 'All', value: null },
    { label: 'Info', value: 'info' },
    { label: 'Success', value: 'success' },
    { label: 'Warning', value: 'warning' },
    { label: 'Error', value: 'error' },
  ];

  selectedType: string | null = null;

  notifications = [
    {
      message: 'Session successfully submitted.',
      type: 'success',
      timestamp: new Date('2025-04-02T10:15:00')
    },
    {
      message: 'Effluent volume unusually low.',
      type: 'warning',
      timestamp: new Date('2025-04-01T17:30:00')
    },
    {
      message: 'Missing systolic data.',
      type: 'error',
      timestamp: new Date('2025-03-30T08:45:00')
    },
    {
      message: 'New guideline available.',
      type: 'info',
      timestamp: new Date('2025-03-28T14:00:00')
    }
  ];
  filteredNotifications() {
    if (!this.selectedType) return this.notifications;
    return this.notifications.filter(n => n.type === this.selectedType);
  }
}
