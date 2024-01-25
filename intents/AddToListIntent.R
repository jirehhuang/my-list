## slots, for reference
add_slot <- c("add")
add_grocery_slot <- c("add item", "add grocery", "add ingredient", "add a reminder to buy", "remind me to buy")
add_task_slot <- c("add task", "add a reminder to", "remind me to")
to_slot <- c("to list", "to my list",
             "to shopping list", "to my shopping list",
             "to to do list", "to my to do list",
             "to check list", "to my check list")
contact_slot <- c("contact", "text", "call", "email", "respond to", "reach out to")
purpose_slot <- c("work")


## template
temp <- c("{add} {item}{to} from {suggested} for {purpose}{due}",
          "{add} {item}{to} for {purpose} from {suggested}{due}",
          "{add} {item}{to} from {suggested}{due}",
          "{add} {item}{to} for {purpose}{due}",
          "{add} {item}{to}{due}")


due_options <- c("", 
                 sprintf(" {%s}", c("due_date", "due_time", "due_day")),
                 sprintf(" due {%s}", c("due_date", "due_time", "due_day")),
                 sprintf(" by {%s}", c("due_date", "due_time", "due_day")))


eg <- expand.grid(add = sprintf("{%s}", c("add_slot", "add_grocery_slot")),  # add_task_slot only attached to item_query
                  item = sprintf("{%s}", c("item_dessert", "item_drink", "item_food")),  # item_food_est is very general
                  to = c("", sprintf(" {%s}", "to_slot")),
                  purpose = sprintf("{%s}", c("purpose_dessert", "purpose_drink", "purpose_food", "purpose_recipe", "purpose_slot")),
                  suggested = sprintf("{%s}", c("suggested_corporation", "suggested_food_est", "suggested_local")),
                  due = due_options)


samples <- unique(c(
  unlist(
    sapply(seq_len(nrow(eg)), function(x){
      
      egx <- eg[x,,drop = FALSE]
      
      sapply(temp, glue::glue, 
             .envir = as.environment(egx))
    })),
  sprintf("%s {name_slot}", c("add {contact_slot}", "add a reminder to {contact_slot}", "remind me to {contact_slot}")),
  # sprintf("%s {task_food_est}", c(add_task_slot)),  # TODO:
  sprintf("%s {item_query}", c("add", add_task_slot))
))
print(length(samples))

write.table(x = data.frame(samples), file = "intents/AddToListIntent-my-list.txt", 
            col.names = FALSE, row.names = FALSE, quote = FALSE)

# samples <- samples[!grepl("", samples)]
