import { BehaviorSubject, of } from "rxjs";
import { LearningHouseError } from "../../models/api.model";

export class AbstractFormResponse {
    success$ = new BehaviorSubject<boolean>(false);

    error$ = new BehaviorSubject<string | null>(null);

    constructor(public successMessage: string) { }

    handleSuccess() {
        this.error$.next(null);
        this.success$.next(true);
        return of(true);
    }

    handleError(error: LearningHouseError) {
        this.success$.next(false);
        this.error$.next(error.key);
        return of(false);
    }

}