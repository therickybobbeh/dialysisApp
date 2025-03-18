import { Component } from '@angular/core';
import {TabPanel, TabView} from "primeng/tabview";
import {NotificationsComponent} from "../../Components/notifications/notifications.component";
import {TableModule} from "primeng/table";
import {InputText} from "primeng/inputtext";
import { PatientTableCard} from "../../Models/tables";

@Component({
  selector: 'app-provider-portal',
  imports: [
    TabView,
    TabPanel,
    NotificationsComponent,
    TableModule,
    InputText
  ],
  templateUrl: './provider-portal.component.html',
  styleUrl: './provider-portal.component.scss'
})
export class ProviderPortalComponent {
  patients: PatientTableCard[] = [
    { name: 'John Doe', age: 45, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-01' },
    { name: 'Jane Smith', age: 50, alerts: 'High BP', lastStatus: 'Critical', lastSession: '2023-10-02' },
    { name: 'Alice Johnson', age: 60, alerts: 'Diabetes', lastStatus: 'Stable', lastSession: '2023-10-03' }
  ];

  selectedPatients: PatientTableCard[] = [];

  activeIndex: number = 0;

  setActiveIndex(index: number) {
    this.activeIndex = index;
  }

  onFilter(event: Event) {
    const input = event.target as HTMLInputElement;
    const value = input.value;
    // Implement filter logic here
  }
}
