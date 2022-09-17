import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map, Observable } from 'rxjs';
import { APIKeyModel } from 'src/app/shared/models/auth.model';
import { AuthService } from '../../auth.service';

@Component({
  selector: 'learninghouse-apikeys',
  templateUrl: './apikeys.component.html',
  styleUrls: ['./apikeys.component.scss']
})
export class APIKeysComponent implements AfterViewInit {

  apikeys: APIKeyModel[] = [];
  dataSource = new MatTableDataSource<APIKeyModel>();

  displayedColumns = ['description', 'role', 'actions'];

  @ViewChild('sort') sort!: MatSort;

  constructor(private authService: AuthService, private translateService: TranslateService) {
  }

  ngAfterViewInit(): void {
    this.loadData();
    this.dataSource.sort = this.sort;
  }

  loadData(): void {
    this.authService.getAPIKeys()
      .pipe(
        map((apikeys) => {
          this.apikeys = apikeys;
          const translatedAPIKeys: APIKeyModel[] = [];
          apikeys.forEach((apikey) => {
            translatedAPIKeys.push({
              description: apikey.description,
              role: this.translateService.instant('common.role.' + apikey.role)
            });
          })
          this.dataSource.data = translatedAPIKeys;
        })
      )
      .subscribe()
  }

}
