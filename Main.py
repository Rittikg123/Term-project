from Mypass import MyPass

if __name__ == "__main__":
    mypass = MyPass()

    while True:
        print("\n 1. Register 2. Add 3. View Vault 4. Unmask 5. Copy 6. Delete 7. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            mypass.register_account()
        elif choice == "2":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            item_type = input("Enter item type: ").strip()
            data = {}
            while True:
                key = input("Enter field name (or 'finish' to finish): ").strip()
                if key.lower() == "finish":
                    break
                value = input(f"Enter value for {key}: ").strip()
                data[key] = value
            mypass.add_vault_item(item_type, data)
        elif choice == "3":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            mypass.view_vault()
        elif choice == "4":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            index = input("Enter the index of the item to unmask: ").strip()
            if index.isdigit():
                mypass.unmask_item(int(index))
            else:
                print("Invalid input. Please enter a valid index.")
        elif choice == "5":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            index = input("Enter the index of the item: ").strip()
            field = input("Enter the field to copy: ").strip()
            if index.isdigit():
                mypass.copy_to_clipboard(int(index), field)
            else:
                print("Invalid input. Please enter a valid index.")
        elif choice == "6":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            index = input("Enter the index of the item to delete: ").strip()
            if index.isdigit():
                mypass.delete_vault_item(int(index))
                
            else:
                print("Invalid input. Please enter a valid index.")
        elif choice == "7":
            print("Exiting")
            break
        else:
            print("Invalid choice.")
