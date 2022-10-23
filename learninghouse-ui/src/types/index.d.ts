export { };

declare global {
    interface Window {
        __env: {
            apiURL?: string
        };
    }
}