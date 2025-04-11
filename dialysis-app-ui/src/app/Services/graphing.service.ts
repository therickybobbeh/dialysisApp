import { Injectable } from '@angular/core';
import { PatientTableCard } from "../Models/tables";
import { firstValueFrom, filter, take } from "rxjs";
import { AuthService } from "./authentication.service";
import { ProviderService } from './provider.service';
import { DialysisService } from './dialysis.service';
import { DialysisSessionResponse } from "../Models/dialysis";

@Injectable({
  providedIn: 'root'
})
export class GraphingService {
  // You can optionally hold a default date range here if needed.
  dateRange: [Date, Date] = [new Date(), new Date()];

  constructor(
    private authService: AuthService,
    private providerService: ProviderService,
    private dialysisService: DialysisService
  ) {}

  /**
   * Fetch dialysis sessions for a given date range.
   * For providers, this waits until a valid selected patient is available.
   * For patients, it uses the user’s ID.
   */
  async fetchSessions(dateRange: [Date, Date]): Promise<DialysisSessionResponse[] | null> {
    const [startDate, endDate] = dateRange;
    let selectedPatient: PatientTableCard | null = null;

    if (this.authService.getUserRole() === 'provider') {
      try {
        // Wait until a complete (non-null) PatientTableCard is emitted
        selectedPatient = await firstValueFrom(
          this.providerService.getSelectedPatient().pipe(
            filter((patient): patient is PatientTableCard => patient !== null),
            take(1)
          )
        );
      } catch (error) {
        console.error('Error retrieving selected patient:', error);
        return null;
      }
    } else {
      const userId = this.authService.getUserID();
      if (userId === null) {
        console.error('No user ID found in auth service.');
        return null;
      }
      selectedPatient = { id: userId } as PatientTableCard;
    }

    if (!selectedPatient) {
      console.warn('No patient selected. Please select a patient to fetch data.');
      return null;
    }

    try {
      const sessions = await firstValueFrom(
        this.dialysisService.getDialysisSessions(
          startDate.toISOString(),
          endDate.toISOString(),
          selectedPatient.id
        )
      );
      return sessions;
    } catch (error) {
      console.error('Error fetching dialysis sessions:', error);
      return null;
    }
  }
}