library(plumber)
library(ggplot2)

#* @apiTitle Attendance Graph API

#* @filter cors
function(req, res) {
  res$setHeader("Access-Control-Allow-Origin", "*")
  res$setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
  res$setHeader("Access-Control-Allow-Headers", "Content-Type")
  # Handle preflight requests
  if (identical(toupper(req$REQUEST_METHOD), "OPTIONS")) {
    res$status <- 200
    return(list())
  }
  plumber::forward()
}

#* Check if API is running
#* @get /
function() {
  list(status = "online", message = "R Server is running")
}

#* Generate attendance graph for one student
#* @get /generate-graph
#* @serializer json
function(
    Reg_Number,
    Student_Name,
    Total_Classes,
    Attended,
    Percentage
) {
  
  # Convert inputs to correct types
  attended_val <- as.numeric(Attended)
  total_val <- as.numeric(Total_Classes)
  
  # Error handling
  if(is.na(attended_val) || is.na(total_val)) {
     return(list(status = "error", message = "Invalid number format"))
  }

  missed <- total_val - attended_val
  
  # Create data frame
  df <- data.frame(
    Status = c("Attended", "Missed"),
    Classes = c(attended_val, missed)
  )
  
  # Generate Plot
  p <- ggplot(df, aes(x = "", y = Classes, fill = Status)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y") +
    theme_void() +
    scale_fill_manual(values = c("#4CAF50", "#F44336")) +
    # Add count labels centered on each slice
    geom_text(aes(label = Classes), position = position_stack(vjust = 0.5), color = "white", size = 5, fontface = "bold") +
    labs(
      title = paste0(
        Student_Name,
        " (", Reg_Number, ")\nAttendance: ",
        Percentage, "%"
      )
    )
  
  # Save Plot
  dir.create("charts", showWarnings = FALSE)
  # Sanitize filename
  safe_reg <- gsub("[^a-zA-Z0-9]", "_", Reg_Number)
  file_path <- paste0("charts/", safe_reg, ".png")
  
  ggsave(file_path, p, width = 5, height = 5)
  
  # Encode to Base64
  if (!requireNamespace("base64enc", quietly = TRUE)) {
      return(list(status = "error", message = "Package 'base64enc' not found. Please run install.packages('base64enc')"))
  }
  
  img_base64 <- base64enc::base64encode(file_path)
  
  list(
    status = "success",
    image_base64 = img_base64
  )
}
