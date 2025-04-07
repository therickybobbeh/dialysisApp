import { Component } from '@angular/core';
import {Toolbar} from 'primeng/toolbar';
import {Button, ButtonDirective, ButtonModule} from 'primeng/button';
import {MeasurementsComponent} from '../../Components/measurements/measurements.component';
import {FooterComponent} from '../../Components/footer/footer.component';
import {NutritionComponent} from '../../Components/nutrition/nutrition.component';
import {GraphingComponent} from '../../Components/graphing/graphing.component';
import {NotificationsComponent} from '../../Components/notifications/notifications.component';
import {NavBarComponent} from '../../Components/nav-bar/nav-bar.component';
import {Image} from 'primeng/image';
import {BloodPressureComponent} from "../../Components/graphing/blood-pressure/blood-pressure.component";
import {
  DialysisMeasurementsGraphComponent
} from "../../Components/graphing/dialysis-measurements-graph/dialysis-measurements-graph.component";
import {TabPanel, TabView} from "primeng/tabview";
import {WeightComponent} from "../../Components/graphing/weight/weight.component";

@Component({
  selector: 'app-patient-portal',
    imports: [
        Toolbar,
        ButtonDirective,
        Button,
        ButtonModule,
        MeasurementsComponent,
        FooterComponent,
        NutritionComponent,
        GraphingComponent,
        NotificationsComponent,
        NavBarComponent,
        Image,
        BloodPressureComponent,
        DialysisMeasurementsGraphComponent,
        TabPanel,
        TabView,
        WeightComponent
    ],
  templateUrl: './patient-portal.component.html',
  styleUrl: './patient-portal.component.scss'
})
export class PatientPortalComponent {

}
