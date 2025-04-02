import {Component} from '@angular/core';
import {ButtonDirective, ButtonIcon, ButtonLabel} from "primeng/button";
import {Toolbar} from "primeng/toolbar";
import {NgStyle} from "@angular/common";
import {Router} from "@angular/router";
import {AuthService} from "../../Services/authentication.service";

@Component({
    selector: 'app-nav-bar',
    imports: [
        ButtonDirective,
        Toolbar,
        NgStyle,
        ButtonIcon,
        ButtonLabel
    ],
    templateUrl: './nav-bar.component.html',
    styleUrl: './nav-bar.component.scss'
})
export class NavBarComponent {
    constructor(private router: Router, private authService: AuthService) {
    }

    logout(): void {
        this.authService.logout();
    }
}