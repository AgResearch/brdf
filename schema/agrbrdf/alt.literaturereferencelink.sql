--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY literaturereferencelink
    ADD CONSTRAINT "$1" FOREIGN KEY (literaturereferenceob) REFERENCES literaturereferenceob(obid);


