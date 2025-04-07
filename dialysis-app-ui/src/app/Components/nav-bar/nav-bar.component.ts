import {Component, OnInit, OnDestroy} from '@angular/core';
import {ButtonDirective, ButtonIcon, ButtonLabel} from "primeng/button";
import {Toolbar} from "primeng/toolbar";
import {NgStyle} from "@angular/common";
import {Router, NavigationEnd, NavigationStart} from "@angular/router";
import {AuthService} from "../../Services/authentication.service";
import {Subscription} from 'rxjs';

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
export class NavBarComponent implements OnInit, OnDestroy {
    protected title = 'Portal';
    private routerSubscription: Subscription = new Subscription();

    constructor(private router: Router, private authService: AuthService) {
    }

    ngOnInit() {
        this.routerSubscription.add(this.router.events.subscribe(event => {
            console.log("event" + event);
            if (event instanceof NavigationEnd) {
                if (event.urlAfterRedirects.includes('provider')) {
                    this.title = 'Provider Portal';
                } else if (event.urlAfterRedirects.includes('patient')) {
                    this.title = 'Patient Portal';
                } else {
                    this.title = 'Portal';
                }
            }
        }));
    }

    ngOnDestroy() {
        this.routerSubscription.unsubscribe();
    }

    logout(): void {
        this.authService.logout();
    }
}