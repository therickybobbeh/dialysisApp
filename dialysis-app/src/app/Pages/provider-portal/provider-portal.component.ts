import { Component } from '@angular/core';
import {TabPanel, TabView} from "primeng/tabview";
import {NotificationsComponent} from "../../Components/notifications/notifications.component";

@Component({
  selector: 'app-provider-portal',
  imports: [
    TabView,
    TabPanel,
    NotificationsComponent
  ],
  templateUrl: './provider-portal.component.html',
  styleUrl: './provider-portal.component.scss'
})
export class ProviderPortalComponent {
  activeIndex: number = 0;

  setActiveIndex(index: number) {
    this.activeIndex = index;
  }
}
