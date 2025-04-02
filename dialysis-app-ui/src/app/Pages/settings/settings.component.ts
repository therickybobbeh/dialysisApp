import { Component } from '@angular/core';
import {Button} from "primeng/button";

@Component({
  selector: 'app-settings',
    imports: [
        Button
    ],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss'
})
export class SettingsComponent {

  toggleDarkMode() {
    const element = document.querySelector('html');
    // TODO: fix later
    // @ts-ignore
    // element.classList.toggle('my-app-dark');
  }
}
