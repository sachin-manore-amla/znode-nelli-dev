# Choosing the shipping and billing address of a cart, order or quote

Files in this folder: 01 functional · 03 admin · 04 webstore · 05 Commerce Portal · 06 API · 07 functions · 08 database


## 1. What it is
At checkout (and when staff build or edit an order), you pick which saved address the order ships to and which one it bills to. The order keeps its own **copy** of each chosen address.

## 2. Where
| Where | How |
|---|---|
| Webstore cart and checkout | the Shipping Address and Billing Address drop-downs (or the search box, see address suggestion) |
| Admin Create Order / Create Quote | the shipping and billing drop-downs under the customer |
| Commerce Portal Edit Order | Ship To (Shipping panel) and Bill To (Payment panel), then Save |
| Admin Manage Order | see change the address on an order |

## 3. Who can pick another address
| Who | Webstore | Admin (for them) | Commerce Portal (for them) |
|---|---|---|---|
| Shopper without an account | Yes | Yes | Yes |
| Account Administrator | Yes | Yes | Yes |
| Account Manager | Yes | Yes | Yes |
| Account User / other role | **No** (the list is locked to the default) | Yes, after confirming a pop-up | Yes |
| Store staff impersonating on the webstore | Yes | — | — |

## 4. What is offered
- The shopper's saved addresses — for account users, the **account's** addresses — that can be used on that side (shipping or billing), plus any one-time address entered in this session.
- The default shipping and default billing addresses are preselected.

## 5. What is allowed and what is not
- Picking an address does not change the address book on the webstore or in the Commerce Portal. In the **admin**, picking an address also re-saves that address from the screen (the update rules of edit address apply).
- The order keeps a copy: later changes to the address book do not change the order.
- In the Commerce Portal the order cannot be saved with a shipping address that does not belong to the order's customer or their account ("The provided address reference is invalid for the specified user."), unless it is a one-time address.
- A Commerce Portal or webstore choice of an address that belongs to someone else is recorded in a technical log, but the copy still happens.
- In the admin, when the store's address check is on, an invalid US address is refused ("Your Shipping Address is not a valid address. Please enter a valid address to continue.").

## 6. Messages
| Message | Where | When |
|---|---|---|
| "Invalid or expired checkout session. Please return to cart and try again." | Webstore | the checkout session reference is missing |
| "Ship to address is required" / "Shipping method is required" / "In-hands date is required" / "Please add at least one product in cart to get the shipping method(s)." | Commerce Portal Shipping panel | saving without them |
| "Shipping Info saved successfully." / "Failed to save Shipping Info" | Commerce Portal | saved / failed |
| "Payment Info saved successfully." / "Failed to save Payment Info" | Commerce Portal | saved / failed |
| "The provided address reference is invalid for the specified user." | Commerce Portal order save | the shipping address is not the customer's or the account's |
| "The selected shipping method is no longer available. Please choose another shipping method to proceed." | API | the chosen shipping method is no longer offered |
| The role pop-up for User customers | Admin | changing a drop-down for a B2B User |

## 7. How it differs
- **By role** — section 3.
- **With or without an account** — account users choose among the account's addresses.
- **By country / setting** — only the admin address check (store feature "Address Validation", US only) changes anything.

## 8. What can be combined
The same address can be both the shipping and the billing address of an order.

## 9. What it changes elsewhere
A new shipping address refreshes shipping methods and prices; the order's totals (and later its tax) follow the chosen addresses.

## 10. Quick answers
- **Which APIs save the choice on the webstore?** Commerce API "shippings / order-shipment" (shipping address) and "payments" (billing address).
- **Why can't a B2B User change the shipping address at checkout?** The drop-down is locked for the User role; only the default is used.
- **Does changing the address book change an existing order?** No.

## 11. What could not be settled
The save calls were not run live: they change real carts or orders.

## 12. For developers
03 admin, 04 webstore, 05 Commerce Portal, 06 API, 07 functions, 08 database.
