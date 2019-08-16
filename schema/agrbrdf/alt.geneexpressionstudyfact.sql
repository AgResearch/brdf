--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneexpressionstudyfact
    ADD CONSTRAINT "$1" FOREIGN KEY (geneexpressionstudy) REFERENCES geneexpressionstudy(obid);


