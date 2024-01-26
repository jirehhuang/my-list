## notes
## AMAZON.FoodEstablishment is really broad, so only use it in replacement for AMAZON.SearchQuery when using multiple slots
## Grocery category: add_grocery_slot, item_dessert, item_drink, item_food
## Task category: add_task_slot, item_query, task_food_est, contact_slot
## Work category (overwrite Task): category_work


## slots, for reference
add_slot <- c("add")
add_grocery_slot <- c("add item", "add grocery", "add ingredient", 
                      "add a reminder to buy", "remind me to buy")  # these two don't really work because task_food_est
add_task_slot <- c("add task", "add a reminder to", "remind me to")
to_slot <- c("to list", "to my list",
             "to shopping list", "to my shopping list",
             "to to do list", "to my to do list",
             "to check list", "to my check list")
contact_slot <- c("contact", "text", "call", "email", "respond to", "reply to", "reach out to", "connect with", "touch base with")
category_work <- c("work")


## template
temp <- c("{add} {item}{to} from {suggested} for {purpose}{due}",
          "{add} {item}{to} for {purpose} from {suggested}{due}",
          "{add} {item}{to} from {suggested}{due}",
          "{add} {item}{to} for {purpose}{due}",
          "{add} {item}{to}{due}")


due_slots <- c("due_date", "due_time", "due_day")  # TODO: due_duration; can't trigger

due_options <- c(
  sapply(c("", "due ", "by ", "at ", "on ", "in ", "within "), function(x){
    
    sprintf(" %s{%s}", x, due_slots)
  })
)


eg <- expand.grid(add = sprintf("{%s}", c("add_slot", "add_grocery_slot")),  # add_task_slot only attached to item_query
                  item = sprintf("{%s}", c("item_dessert", "item_drink", "item_food")),  # item_food_est is very general
                  to = c("", sprintf(" {%s}", "to_slot")),
                  purpose = sprintf("{%s}", c("purpose_dessert", "purpose_drink", "purpose_food", "purpose_recipe")),
                  suggested = sprintf("{%s}", c("suggested_corporation", "suggested_local")),
                  due = c("", due_options))

utter_grocery <- unique(c(unlist(
  sapply(seq_len(nrow(eg)), function(x){
    
    egx <- eg[x,,drop = FALSE]
    
    sapply(temp, glue::glue, 
           .envir = as.environment(egx))
  })
)))


utter_task <- c(
  unlist(sapply(sprintf("{%s}", c("add_slot", "add_task_slot")), function(x){
    unlist(sapply(c("", " for {category_work}"), function(y){
      unique(c(sprintf("%s {task_food_est}%s%s", x, due_options, y),
               sprintf("%s {task_food_est}%s%s", x, y, due_options),
               sprintf("%s {contact_slot} {name_slot}%s%s", x, due_options, y),
               sprintf("%s {contact_slot} {name_slot}%s%s", x, y, due_options)))
    }))
  })),
  sprintf("%s {item_query}", c(add_slot, add_task_slot))  # can only have one slot
)


utter <- c(utter_grocery, 
           utter_task)


print(length(utter))


write.table(x = data.frame(utter), file = "intents/AddToListIntent-utterances.txt", 
            col.names = FALSE, row.names = FALSE, quote = FALSE)
