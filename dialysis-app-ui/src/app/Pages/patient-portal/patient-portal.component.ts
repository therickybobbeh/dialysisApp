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
    Image
  ],
  templateUrl: './patient-portal.component.html',
  styleUrl: './patient-portal.component.scss'
})
export class PatientPortalComponent {

}
