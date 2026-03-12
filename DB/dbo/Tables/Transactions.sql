CREATE TABLE [dbo].[Transactions] (
    [TransactionId]   INT             IDENTITY (1, 1) NOT NULL,
    [UserId]          INT             NOT NULL,
    [Amount]          DECIMAL (18, 2) NOT NULL,
    [Type]            NVARCHAR (10)   NOT NULL,
    [Category]        NVARCHAR (100)  NOT NULL,
    [Description]     NVARCHAR (500)  NULL,
    [TransactionDate] DATETIME2 (7)   DEFAULT (getdate()) NOT NULL,
    [CreatedAt]       DATETIME2 (7)   DEFAULT (getdate()) NOT NULL,
    PRIMARY KEY CLUSTERED ([TransactionId] ASC),
    CHECK ([Type]='Expense' OR [Type]='Income'),
    FOREIGN KEY ([UserId]) REFERENCES [dbo].[Users] ([UserId]) ON DELETE CASCADE
);


GO
CREATE NONCLUSTERED INDEX [IX_Transactions_UserId]
    ON [dbo].[Transactions]([UserId] ASC);


GO
CREATE NONCLUSTERED INDEX [IX_Transactions_Date]
    ON [dbo].[Transactions]([TransactionDate] ASC);

