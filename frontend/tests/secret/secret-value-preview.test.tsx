import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SecretValuePreview } from "@/features/secret/components/secret-value-preview";

let pathname = "/vaults/vault_1/projects/project_1/secrets/secret_1";

vi.mock("next/navigation", () => ({
  usePathname: () => pathname,
}));

describe("SecretValuePreview", () => {
  beforeEach(() => {
    pathname = "/vaults/vault_1/projects/project_1/secrets/secret_1";
    localStorage.clear();
    sessionStorage.clear();
  });

  it("reveals only after explicit action and clears on hide", async () => {
    const user = userEvent.setup();
    const onReveal = vi.fn(async () => ({ value: "sensitive-value" }));

    render(<SecretValuePreview onReveal={onReveal} />);

    expect(screen.queryByText("sensitive-value")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /reveal value/i }));

    expect(await screen.findByText("sensitive-value")).toBeInTheDocument();
    expect(onReveal).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem("sensitive-value")).toBeNull();
    expect(sessionStorage.getItem("sensitive-value")).toBeNull();

    await user.click(screen.getByRole("button", { name: /hide/i }));

    await waitFor(() => expect(screen.queryByText("sensitive-value")).not.toBeInTheDocument());
  });

  it("does not reveal when the backend permission summary denies it", () => {
    const onReveal = vi.fn(async () => ({ value: "sensitive-value" }));

    render(<SecretValuePreview canReveal={false} onReveal={onReveal} />);

    expect(screen.getByRole("button", { name: /reveal value/i })).toBeDisabled();
    expect(onReveal).not.toHaveBeenCalled();
  });
});
