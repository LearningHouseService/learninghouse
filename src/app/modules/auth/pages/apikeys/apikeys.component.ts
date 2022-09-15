import { Component } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { map, Observable } from 'rxjs';
import { APIKeyModel } from 'src/app/shared/models/auth.model';
import { AuthService } from '../../auth.service';

@Component({
  selector: 'learninghouse-apikeys',
  templateUrl: './apikeys.component.html',
  styleUrls: ['./apikeys.component.scss']
})
export class APIKeysComponent {

  private dataSource = new MatTableDataSource<APIKeyModel>();

  apikeysDataSource$: Observable<MatTableDataSource<APIKeyModel>> =
    this.authService.apikeys.
      pipe(
        map((apikeys) => {
          const dataSource = this.dataSource;
          dataSource.data = apikeys;
          return dataSource;
        })
      )

  displayedColumns = ['description', 'role'];

  constructor(private authService: AuthService) {
    this.authService.getAPIKeys();
  }


}
