import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { provideAnimations } from '@angular/platform-browser/animations';
import {importProvidersFrom} from "@angular/core";
import {HttpClientModule, provideHttpClient, withInterceptorsFromDi} from "@angular/common/http";

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient(withInterceptorsFromDi()),
      provideAnimations(), ...appConfig.providers]
}).catch(err => console.error(err));
