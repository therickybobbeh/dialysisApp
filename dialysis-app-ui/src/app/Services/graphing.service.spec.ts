import { TestBed } from '@angular/core/testing';

import { GraphingService } from './graphing.service';

describe('GraphingService', () => {
  let service: GraphingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GraphingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
