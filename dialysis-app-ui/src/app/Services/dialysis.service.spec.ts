import { TestBed } from '@angular/core/testing';

import { DialysisService } from './dialysis.service';

describe('PatientsService', () => {
  let service: DialysisService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DialysisService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
