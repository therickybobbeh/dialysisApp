import {Component, OnInit, OnDestroy} from '@angular/core';
import {NgClass, NgForOf, NgIf} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {DropdownModule} from 'primeng/dropdown';
import {DatePipe} from '@angular/common';
import {Tooltip} from 'primeng/tooltip';
import {filter, Observable, of, Subscription, switchMap} from 'rxjs';
import {
    mapBackendDataToPatientAlerts,
    PatientAlertsBackend,
    PatientAlertsFrontend,
    AlertType
} from '../../Models/notifications';
import {NotificationsService} from '../../Services/notifications.service';
import {ProviderService} from '../../Services/provider.service';
import {PatientTableCard} from '../../Models/tables';
import {AuthService} from "../../Services/authentication.service";

interface NotificationItem {
    key: keyof PatientAlertsFrontend;
    message: string;
    type: AlertType;
    timestamp?: Date;
}

@Component({
    selector: 'app-notifications',
    templateUrl: './notifications.component.html',
    styleUrls: ['./notifications.component.scss'],
    imports: [
        NgClass, NgForOf, NgIf,
        FormsModule, DropdownModule,
        DatePipe,
        Tooltip
    ]
})
export class NotificationsComponent implements OnInit, OnDestroy {
    notificationTypes = [
        {label: 'All', value: 'all'},
        {label: 'Critical', value: 'critical'},
        {label: 'Monitor', value: 'monitor'},
        {label: 'Information', value: 'information'}
    ];
    selectedType = 'all';
    originalNotifications: NotificationItem[] = [];
    private lastBackend: PatientAlertsBackend | null = null;
    private subscriptions = new Subscription();
    private currentPatient: PatientTableCard | null = null;

    private frontendToBackend: Record<keyof PatientAlertsFrontend, keyof PatientAlertsBackend> = {
        lowBloodPressure: 'lowBloodPressure',
        highBloodPressure: 'highBloodPressure',
        dialysisGrowthAdjustment: 'dialysisGrowthAdjustment',
        fluidOverloadHigh: 'fluidOverloadHigh',
        fluidOverloadWatch: 'fluidOverloadWatch',
        effluentVolume: 'effluentVolume',
        protein: 'protein'
    };

    constructor(
        private notificationsService: NotificationsService,
        private providerService: ProviderService,
        private authService: AuthService
    ) {
    }

    ngOnInit(): void {
        const role = this.authService.getUserRole();

        const trigger$: Observable<null | PatientTableCard> = role === 'provider'
            ? this.providerService.getSelectedPatient().pipe(
                filter((patient): patient is PatientTableCard => patient !== null)
            )
            : of({
                id: this.authService.getUserID(),
            } as PatientTableCard);

        // Initial load from selection
        this.subscriptions.add(
            trigger$.pipe(
                switchMap((patient: PatientTableCard | null) => {
                    this.currentPatient = patient;
                    return this.notificationsService.getNotifications();
                })
            )
                .subscribe({
                    next: (data: PatientAlertsBackend) => {
                        this.lastBackend = {...data};
                        this.originalNotifications = this.mapNotifications(data);
                    },
                    error: (err: unknown) => console.error('Error loading notifications:', err)
                })
        );

        // Reload on trigger
        this.subscriptions.add(
            this.notificationsService.triggerNotificationReload$
                .pipe(
                    switchMap(() => this.notificationsService.getNotifications())
                )
                .subscribe({
                    next: (data: PatientAlertsBackend) => {
                        this.lastBackend = {...data};
                        this.originalNotifications = this.mapNotifications(data);
                    },
                    error: (err: unknown) => console.error('Error reloading notifications:', err)
                })
        );
    }

    ngOnDestroy() {
        this.subscriptions.unsubscribe();
        this.originalNotifications = [];
        this.currentPatient = null;
        this.lastBackend = null;
        this.selectedType = 'all';
    }

    private mapNotifications(data: PatientAlertsBackend): NotificationItem[] {
        const frontend = mapBackendDataToPatientAlerts(data);
        return (Object.keys(frontend) as (keyof PatientAlertsFrontend)[])
            .map(key => ({
                key,
                message: frontend[key].message,
                type: frontend[key].type,
                timestamp: new Date() // TODO: real timestamp
            }))
            .filter(n => n.type !== null) as NotificationItem[];
    }

    filteredNotifications(): NotificationItem[] {
        if (this.selectedType === 'all') {
            return this.originalNotifications;
        }
        return this.originalNotifications.filter(n => n.type === this.selectedType);
    }

    dismissOne(item: NotificationItem) {
        if (!this.lastBackend || !this.currentPatient) return;
        const backendKey = this.frontendToBackend[item.key];
        this.lastBackend[backendKey] = false;
        this.notificationsService
            .updateNotifications(this.lastBackend, this.currentPatient.id)
            .subscribe({
                next: () => {
                    this.originalNotifications = this.originalNotifications.filter(n => n.key !== item.key);
                },
                error: err => {
                    console.error('Error dismissing notification:', err);
                }
            });
    }

    dismissAll() {
        if (!this.lastBackend || !this.currentPatient) return;
        for (const fk of Object.values(this.frontendToBackend)) {
            this.lastBackend[fk] = false;
        }
        this.notificationsService
            .updateNotifications(this.lastBackend, this.currentPatient.id)
            .subscribe({
                next: () => {
                    this.originalNotifications = [];
                },
                error: err => {
                    console.error('Error dismissing all notifications:', err);
                }
            });
    }
}