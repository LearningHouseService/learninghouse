import { Component, EventEmitter, Input, OnDestroy, OnInit, Output } from '@angular/core';
import { BehaviorSubject, ReplaySubject, interval, takeUntil } from 'rxjs';

@Component({
  selector: 'learninghouse-session-timer',
  templateUrl: './session-timer.component.html',
  styleUrls: ['./session-timer.component.scss']
})
export class SessionTimerComponent implements OnInit, OnDestroy {
  @Input()
  expires: Date | null = null;

  @Output()
  finished = new EventEmitter<void>();

  @Output()
  refresh = new EventEmitter<void>();

  display$ = new BehaviorSubject<string>('00 m 00 s');

  private destroyed$: ReplaySubject<boolean> = new ReplaySubject(1);

  ngOnInit(): void {
    interval(1000)
      .pipe(takeUntil(this.destroyed$))
      .subscribe(() => { this.calculateTime() })
  }

  calculateTime(): void {
    let timeDifference = 0;
    if (this.expires) {
      timeDifference = this.expires.getTime() - new Date().getTime();
      if (Math.floor(timeDifference / 1000) <= 0) {
        this.finished.emit();
      }
    }

    const seconds = Math.floor((timeDifference) / (1000) % 60);
    const minutes = Math.floor((timeDifference) / (60000) % 60);
    this.display$.next(String(minutes).padStart(2, '0') + ' m ' + String(seconds).padStart(2, '0') + ' s');
  }

  ngOnDestroy(): void {
    this.destroyed$.next(true);
    this.destroyed$.complete();
  }

}
