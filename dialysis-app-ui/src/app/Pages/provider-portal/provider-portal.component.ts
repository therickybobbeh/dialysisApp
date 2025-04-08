import { Component } from '@angular/core';
import {NotificationsComponent} from "../../Components/notifications/notifications.component";
import {TableModule} from "primeng/table";
import { PatientTableCard} from "../../Models/tables";
import {NavBarComponent} from "../../Components/nav-bar/nav-bar.component";
import {MeasurementsComponent} from "../../Components/measurements/measurements.component";
import {
  DialysisMeasurementsGraphComponent
} from "../../Components/graphing/dialysis-measurements-graph/dialysis-measurements-graph.component";
import {BloodPressureComponent} from "../../Components/graphing/blood-pressure/blood-pressure.component";
import {WeightComponent} from "../../Components/graphing/weight/weight.component";
import {Tabs, TabsModule} from "primeng/tabs";
import {TabPanel, TabView} from "primeng/tabview";
import {PatientListComponent} from "../../Components/patient-list/patient-list.component";

@Component({
  selector: 'app-provider-portal',
  imports: [
    NotificationsComponent,
    TableModule,
    NavBarComponent,
    MeasurementsComponent,
    DialysisMeasurementsGraphComponent,
    BloodPressureComponent,
    WeightComponent,
    TabsModule,
    Tabs,
    TabPanel,
    TabView,
    PatientListComponent
  ],
  templateUrl: './provider-portal.component.html',
  styleUrl: './provider-portal.component.scss'
})
export class ProviderPortalComponent {
  //TODO: remove this mock data

}
