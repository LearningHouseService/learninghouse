import { Component, OnInit } from '@angular/core';
import { BehaviorSubject, catchError, map, of } from 'rxjs';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { VersionItem } from 'src/app/shared/models/api.model';
import { APIService } from 'src/app/shared/services/api.service';
import { AppService } from 'src/app/shared/services/app.service';


@Component({
  selector: 'lh-info-dialog',
  templateUrl: './info-dialog.component.html',
  styleUrls: ['./info-dialog.component.scss']
})
export class InfoDialogComponent implements OnInit {

  versions$ = new BehaviorSubject<VersionItem[] | null>(null);

  constructor(
    public api: APIService,
    public appService: AppService,
    public auth: AuthService) { }

  ngOnInit(): void {
    this.api.update_mode();

    this.api.versions()
      .pipe(
        map((versions) => {
          this.versions$.next(versions)
        }),
        catchError(() => {
          this.versions$.next(null)
          return of(false);
        }))
      .subscribe();
  }

}
