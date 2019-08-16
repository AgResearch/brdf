--
-- Name: literaturereferenceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE literaturereferenceob FROM PUBLIC;
REVOKE ALL ON TABLE literaturereferenceob FROM agrbrdf;
GRANT ALL ON TABLE literaturereferenceob TO agrbrdf;
GRANT SELECT ON TABLE literaturereferenceob TO gbs;


