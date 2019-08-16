--
-- Name: literaturereferencelink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE literaturereferencelink FROM PUBLIC;
REVOKE ALL ON TABLE literaturereferencelink FROM agrbrdf;
GRANT ALL ON TABLE literaturereferencelink TO agrbrdf;
GRANT SELECT ON TABLE literaturereferencelink TO gbs;


