import { Component } from '@angular/core';
import {ButtonDirective} from "primeng/button";
import {Toolbar} from "primeng/toolbar";

@Component({
  selector: 'app-nav-bar',
    imports: [
        ButtonDirective,
        Toolbar
    ],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.scss'
})
export class NavBarComponent {

}
