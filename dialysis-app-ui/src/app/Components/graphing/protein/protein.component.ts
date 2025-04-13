import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { ChartModule } from 'primeng/chart';
import { FormsModule} from "@angular/forms";
import { DatePicker } from 'primeng/datepicker';
import { ChartData, ChartOptions } from 'chart.js';
import { DialysisSessionResponse } from '../../../Models/dialysis';
import { GraphingService } from '../../../Services/graphing.service';
import { ProviderService } from '../../../Services/provider.service';

@Component({
  selector: 'app-protein',
  imports: [ChartModule, FormsModule, DatePicker],
  templateUrl: './protein.component.html',
  styleUrls: ['./protein.component.scss']
})
export class ProteinComponent implements OnInit, OnDestroy {
  dateRange: Date[] = [];
  chartData: ChartData<'line'> | undefined;
  chartOptions: ChartOptions<'line'> | undefined;
  private subscriptions = new Subscription();

  constructor(
    private graphingService: GraphingService,
    private providerService: ProviderService
  ) {}

  async ngOnInit() {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 7);
    this.dateRange = [sevenDaysAgo, yesterday];

    this.subscriptions.add(
      this.providerService.getSelectedPatient().subscribe(() => {
        this.fetchDataAndUpdateChart();
      })
    );

    await this.fetchDataAndUpdateChart();
  }

  async fetchDataAndUpdateChart() {
    if (this.dateRange.length !== 2) {
      console.warn('Invalid date range selected.');
      return;
    }

    const sessions = await this.graphingService.fetchSessions(this.dateRange as [Date, Date]);
    if (sessions) {
      this.updateChartData(sessions);
    }
  }

  updateChartData(sessions: DialysisSessionResponse[]) {
    const labels = sessions.map((_, index) => (index + 1).toString());
    const proteinLevels = sessions.map(session => session.protein);
    const sessionDates = sessions.map(session => new Date(session.session_date).toLocaleDateString());
    const sessionTypes = sessions.map(session => session.session_type);

    const dynamicMin = Math.min(...proteinLevels) - 10;
    const dynamicMax = Math.max(...proteinLevels) + 10;

    this.chartData = {
      labels,
      datasets: [
        {
          label: 'Protein Levels',
          data: proteinLevels,
          fill: false,
          borderColor: '#4caf50',
          tension: 0.1
        }
      ]
    };

    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        title: {
          display: true,
          text: 'Protein Levels Over Selected Sessions'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const datasetLabel = context.dataset.label || '';
              const value = context.raw;
              const date = sessionDates[context.dataIndex];
              const type = sessionTypes[context.dataIndex];
              return `${datasetLabel}: ${value} (Date: ${date}, Type: ${type})`;
            }
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: 'Protein Levels (g/dL)' },
          min: dynamicMin,
          max: dynamicMax
        },
        x: {
          title: { display: true, text: 'Session Number' }
        }
      }
    };
  }

  ngOnDestroy() {
    this.subscriptions.unsubscribe();
  }
}