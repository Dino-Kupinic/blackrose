/**
 * Typed errors for the Blackrose decision layer.
 */

export class BlackroseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BlackroseError";
  }
}

export class PolicyConfigError extends BlackroseError {
  constructor(message: string) {
    super(message);
    this.name = "PolicyConfigError";
  }
}

export class GuardClosedError extends BlackroseError {
  constructor(message: string) {
    super(message);
    this.name = "GuardClosedError";
  }
}

/** TypeSafe `systemOne` call failed. Fail closed: do not treat as `allow`. */
export class TypeSafeRequestError extends BlackroseError {
  constructor(message: string, options?: ErrorOptions) {
    super(message);
    this.name = "TypeSafeRequestError";
    if (options?.cause !== undefined) {
      this.cause = options.cause;
    }
  }
}
