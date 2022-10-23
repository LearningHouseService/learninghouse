import { BehaviorSubject, of } from "rxjs";
import { LearningHouseError } from "../../models/api.model";

export class AbstractFormResponse {
    state$ = new BehaviorSubject<string | null>(null);

    handleSuccess() {
        this.state$.next('success');
        return of(true);
    }

    handleError(error: LearningHouseError) {
        this.state$.next(error.key);
        return of(false);
    }

    get isSuccess(): boolean {
        return this.state$.getValue() === 'success';
    }

}