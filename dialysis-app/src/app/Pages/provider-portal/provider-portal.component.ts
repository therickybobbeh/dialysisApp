import { Component } from '@angular/core';
import {TabPanel, TabView} from "primeng/tabview";
import {NotificationsComponent} from "../../Components/notifications/notifications.component";
import {TableModule} from "primeng/table";
import {InputText} from "primeng/inputtext";
import { PatientTableCard} from "../../Models/tables";
import {NavBarComponent} from "../../Components/nav-bar/nav-bar.component";

@Component({
  selector: 'app-provider-portal',
  imports: [
    TabView,
    TabPanel,
    NotificationsComponent,
    TableModule,
    InputText,
    NavBarComponent
  ],
  templateUrl: './provider-portal.component.html',
  styleUrl: './provider-portal.component.scss'
})
export class ProviderPortalComponent {
  //TODO: remove this mock data
  patients: PatientTableCard[] = [
    { name: 'Cumcustador Esquien', age: 45, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-01' },
    { name: 'Jane Smith', age: 50, alerts: 'High BP', lastStatus: 'Critical', lastSession: '2023-10-02' },
    { name: 'Alice Johnson', age: 60, alerts: 'Diabetes', lastStatus: 'Stable', lastSession: '2023-10-03' },
    { name: 'Bob Brown', age: 55, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-04' },
    { name: 'Carol White', age: 65, alerts: 'Low BP', lastStatus: 'Critical', lastSession: '2023-10-05' },
    { name: 'David Green', age: 70, alerts: 'High Cholesterol', lastStatus: 'Stable', lastSession: '2023-10-06' },
    { name: 'Eve Black', age: 75, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-07' },
    { name: 'Frank Blue', age: 80, alerts: 'Heart Disease', lastStatus: 'Critical', lastSession: '2023-10-08' },
    { name: 'Grace Yellow', age: 85, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-09' },
    { name: 'Hank Red', age: 90, alerts: 'Diabetes', lastStatus: 'Stable', lastSession: '2023-10-10' },
    { name: 'Ivy Purple', age: 95, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-11' },
    { name: 'Jack Orange', age: 100, alerts: 'High BP', lastStatus: 'Critical', lastSession: '2023-10-12' },
    { name: 'Kathy Pink', age: 105, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-13' },
    { name: 'Leo Gray', age: 110, alerts: 'Low BP', lastStatus: 'Critical', lastSession: '2023-10-14' },
    { name: 'Mona Brown', age: 115, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-15' },
    { name: 'Nina White', age: 120, alerts: 'High Cholesterol', lastStatus: 'Stable', lastSession: '2023-10-16' },
    { name: 'Oscar Green', age: 125, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-17' },
    { name: 'Paul Black', age: 130, alerts: 'Heart Disease', lastStatus: 'Critical', lastSession: '2023-10-18' },
    { name: 'Quinn Blue', age: 135, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-19' },
    { name: 'Rita Yellow', age: 140, alerts: 'Diabetes', lastStatus: 'Stable', lastSession: '2023-10-20' },
    { name: 'Sam Red', age: 145, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-21' },
    { name: 'Tina Purple', age: 150, alerts: 'High BP', lastStatus: 'Critical', lastSession: '2023-10-22' },
    { name: 'Uma Orange', age: 155, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-23' },
    { name: 'Vince Pink', age: 160, alerts: 'Low BP', lastStatus: 'Critical', lastSession: '2023-10-24' },
    { name: 'Walt Gray', age: 165, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-25' },
    { name: 'Xena Brown', age: 170, alerts: 'High Cholesterol', lastStatus: 'Stable', lastSession: '2023-10-26' },
    { name: 'Yara White', age: 175, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-27' },
    { name: 'Zack Green', age: 180, alerts: 'Heart Disease', lastStatus: 'Critical', lastSession: '2023-10-28' },
    { name: 'Amy Black', age: 185, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-29' },
    { name: 'Ben Blue', age: 190, alerts: 'Diabetes', lastStatus: 'Stable', lastSession: '2023-10-30' },
    { name: 'Cathy Yellow', age: 195, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-10-31' },
    { name: 'Dan Red', age: 200, alerts: 'High BP', lastStatus: 'Critical', lastSession: '2023-11-01' },
    { name: 'Ella Purple', age: 205, alerts: 'None', lastStatus: 'Stable', lastSession: '2023-11-02' }
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
