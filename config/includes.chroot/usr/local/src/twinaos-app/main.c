#include <gtk/gtk.h>
#include <glib.h>

static void
on_activate (GtkApplication *app)
{
    GtkWidget *window;
    GtkWidget *box;
    GtkWidget *label;
    GtkWidget *button;
    
    // Create main window
    window = gtk_application_window_new (app);
    gtk_window_set_title (GTK_WINDOW (window), "TwinaOS Live System");
    gtk_window_set_default_size (GTK_WINDOW (window), 800, 600);
    
    // Create vertical box container
    box = gtk_box_new (GTK_ORIENTATION_VERTICAL, 20);
    gtk_widget_set_margin_start (box, 40);
    gtk_widget_set_margin_end (box, 40);
    gtk_widget_set_margin_top (box, 40);
    gtk_widget_set_margin_bottom (box, 40);
    
    // Create welcome label
    label = gtk_label_new (NULL);
    gtk_label_set_markup (GTK_LABEL (label), 
        "<span size='24000' weight='bold'>Welcome to TwinaOS</span>\n\n"
        "<span size='14000'>Minimal Debian Live System</span>\n"
        "<span size='12000'>Running on Wayland with Cage compositor</span>\n\n"
        "<span size='10000'>Features:</span>\n"
        "<span size='10000'>• Wayland display server</span>\n"
        "<span size='10000'>• PipeWire audio system</span>\n"
        "<span size='10000'>• NetworkManager for connectivity</span>\n"
        "<span size='10000'>• Bluetooth support</span>");
    gtk_label_set_justify (GTK_LABEL (label), GTK_JUSTIFY_CENTER);
    
    // Create a simple button
    button = gtk_button_new_with_label ("System Information");
    gtk_widget_set_size_request (button, 200, 50);
    gtk_widget_set_halign (button, GTK_ALIGN_CENTER);
    
    // Connect button signal
    g_signal_connect_swapped (button, "clicked", 
                              G_CALLBACK (gtk_window_destroy), window);
    
    // Pack widgets into box
    gtk_box_append (GTK_BOX (box), label);
    gtk_box_append (GTK_BOX (box), button);
    
    // Set box as window child
    gtk_window_set_child (GTK_WINDOW (window), box);
    
    // Show the window
    gtk_window_present (GTK_WINDOW (window));
}

static void
on_button_clicked (GtkWidget *button, gpointer user_data)
{
    GtkWidget *dialog;
    GtkWidget *window = GTK_WIDGET(user_data);
    
    dialog = gtk_message_dialog_new (GTK_WINDOW (window),
                                     GTK_DIALOG_DESTROY_WITH_PARENT,
                                     GTK_MESSAGE_INFO,
                                     GTK_BUTTONS_OK,
                                     "TwinaOS System Information");
    
    gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog),
        "Kernel: Linux\n"
        "Display: Wayland\n"
        "Compositor: Cage\n"
        "Audio: PipeWire\n"
        "Base: Debian Bookworm");
    
    gtk_window_present (GTK_WINDOW (dialog));
    
    g_signal_connect (dialog, "response", G_CALLBACK (gtk_window_destroy), NULL);
}

int
main (int argc, char *argv[])
{
    GtkApplication *app;
    int status;
    
    app = gtk_application_new ("org.twinaos.demo", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect (app, "activate", G_CALLBACK (on_activate), NULL);
    
    status = g_application_run (G_APPLICATION (app), argc, argv);
    g_object_unref (app);
    
    return status;
}
