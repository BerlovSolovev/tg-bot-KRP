CREATE TABLE [dbo].[Users] (
    [UserId]       INT            IDENTITY (1, 1) NOT NULL,
    [TelegramId]   BIGINT         NOT NULL,
    [UserName]     NVARCHAR (100) NULL,
    [FirstName]    NVARCHAR (100) NULL,
    [LastName]     NVARCHAR (100) NULL,
    [RegisteredAt] DATETIME2 (7)  DEFAULT (getdate()) NOT NULL,
    [IsActive]     BIT            DEFAULT ((1)) NOT NULL,
    PRIMARY KEY CLUSTERED ([UserId] ASC),
    UNIQUE NONCLUSTERED ([TelegramId] ASC)
);


GO
CREATE NONCLUSTERED INDEX [IX_Users_TelegramId]
    ON [dbo].[Users]([TelegramId] ASC);

