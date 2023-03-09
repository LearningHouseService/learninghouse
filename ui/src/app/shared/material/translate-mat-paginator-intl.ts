import { Injectable, OnDestroy } from '@angular/core';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { TranslateService } from '@ngx-translate/core';
import { takeUntil, Subject, map } from 'rxjs';

@Injectable()
export class TranslateMatPaginatorIntl extends MatPaginatorIntl
    implements OnDestroy {
    unsubscribe: Subject<void> = new Subject<void>();
    OF_LABEL = 'of';

    constructor(private translate: TranslateService) {
        super();

        this.translate.onLangChange
            .pipe(
                takeUntil(this.unsubscribe),
                map(() => {
                    this.getAndInitTranslations();
                })
            )
            .subscribe()

        this.getAndInitTranslations();
    }

    ngOnDestroy() {
        this.unsubscribe.next();
        this.unsubscribe.complete();
    }

    getAndInitTranslations() {
        this.translate
            .get([
                'common.paginator.items_per_page',
                'common.paginator.next_page',
                'common.paginator.previous_page',
                'common.paginator.of_label',
            ])
            .pipe(
                takeUntil(this.unsubscribe)
            )
            .subscribe(translation => {
                this.itemsPerPageLabel =
                    translation['common.paginator.items_per_page'];
                this.nextPageLabel = translation['common.paginator.next_page'];
                this.previousPageLabel =
                    translation['common.paginator.previous_page'];
                this.OF_LABEL = translation['common.paginator.of_label'];
                this.changes.next();
            });
    }

    override getRangeLabel = (
        page: number,
        pageSize: number,
        length: number,
    ) => {
        if (length === 0 || pageSize === 0) {
            return `0 ${this.OF_LABEL} ${length}`;
        }
        length = Math.max(length, 0);
        const startIndex = page * pageSize;
        const endIndex =
            startIndex < length
                ? Math.min(startIndex + pageSize, length)
                : startIndex + pageSize;
        return `${startIndex + 1} - ${endIndex} ${this.OF_LABEL
            } ${length}`;
    };
}