import { Component } from '@angular/core';
import {ButtonDirective} from "primeng/button";
import {Toolbar} from "primeng/toolbar";
import {NgStyle} from "@angular/common";

@Component({
  selector: 'app-nav-bar',
    imports: [
        ButtonDirective,
        Toolbar,
        NgStyle
    ],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.scss'
})
export class NavBarComponent {

}
